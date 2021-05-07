package org.confeti.controllers.core;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.confeti.controllers.dto.ErrorResponse;
import org.confeti.controllers.dto.core.ReportResponse;
import org.confeti.service.ReportService;
import org.confeti.service.dto.Report;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;
import reactor.core.publisher.GroupedFlux;
import reactor.core.publisher.Mono;
import reactor.util.function.Tuple2;

import java.util.Collection;
import java.util.Collections;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.function.Function;

import static org.confeti.controllers.ControllersUtils.CONFERENCE_NAME_URI_PARAMETER;
import static org.confeti.controllers.ControllersUtils.CONTROLLER_MARKER;
import static org.confeti.controllers.ControllersUtils.REST_API_PATH;
import static org.confeti.controllers.ControllersUtils.YEAR_URI_PARAMETER;
import static org.springframework.http.MediaType.APPLICATION_JSON_VALUE;

@RestController
@RequestMapping(value = REST_API_PATH + "/report", produces = APPLICATION_JSON_VALUE)
@RequiredArgsConstructor
@Slf4j
public class ReportController {

    private final ReportService reportService;

    @GetMapping(path = "/stat/tag", params = {YEAR_URI_PARAMETER, CONFERENCE_NAME_URI_PARAMETER})
    @ResponseBody
    public Mono<ResponseEntity<Object>> handleTagRequest(@RequestParam(YEAR_URI_PARAMETER) final int year,
                                                         @RequestParam(CONFERENCE_NAME_URI_PARAMETER) final String conferenceName) {
        logRequest("/stat/tag", String.format("year: %d, conference_name: %s", year, conferenceName));
        return handleRequest(year, conferenceName, Report::getTags)
                .doOnError(ReportController::logError);
    }

    @GetMapping(path = "/stat/tag", params = {CONFERENCE_NAME_URI_PARAMETER})
    @ResponseBody
    public Mono<ResponseEntity<Object>> handleTagRequest(@RequestParam(CONFERENCE_NAME_URI_PARAMETER) final String conferenceName) {
        logRequest("/stat/tag", String.format("conference_name: %s", conferenceName));
        return handleRequest(conferenceName, Report::getTags)
                .doOnError(ReportController::logError);
    }

    @GetMapping(path = "/stat/tag")
    @ResponseBody
    public Mono<ResponseEntity<Object>> handleTagRequest(
            @RequestParam(value = YEAR_URI_PARAMETER, required = false) final Optional<Integer> year) {
        logRequest("/stat/tag", String.format("%s is exists %b", YEAR_URI_PARAMETER, year.isEmpty()));
        return handleRequest(year, Report::getTags)
                .doOnError(ReportController::logError);
    }

    @GetMapping(path = "/stat/language", params = {YEAR_URI_PARAMETER, CONFERENCE_NAME_URI_PARAMETER})
    @ResponseBody
    public Mono<ResponseEntity<Object>> handleLanguageRequest(@RequestParam(YEAR_URI_PARAMETER) final int year,
                                                              @RequestParam(CONFERENCE_NAME_URI_PARAMETER) final String conferenceName) {
        return handleRequest(year, conferenceName, ReportController::languageToSetConverter)
                .doOnError(ReportController::logError);
    }

    @GetMapping(path = "/stat/language", params = {CONFERENCE_NAME_URI_PARAMETER})
    @ResponseBody
    public Mono<ResponseEntity<Object>> handleLanguageRequest(@RequestParam(CONFERENCE_NAME_URI_PARAMETER) final String conferenceName) {
        return handleRequest(conferenceName, ReportController::languageToSetConverter)
                .doOnError(ReportController::logError);
    }

    @GetMapping(path = "/stat/language")
    @ResponseBody
    public Mono<ResponseEntity<Object>> handleLanguageRequest(
            @RequestParam(value = YEAR_URI_PARAMETER, required = false) final Optional<Integer> year) {
        return handleRequest(year, ReportController::languageToSetConverter)
                .doOnError(ReportController::logError);
    }

    private Mono<ResponseEntity<Object>> handleRequest(final int year,
                                                       final String conferenceName,
                                                       final Function<Report, Collection<String>> reportConverter) {
        return countInfo(reportService.findByConference(conferenceName, year), reportConverter)
                .<ResponseEntity<Object>>map(map -> ResponseEntity.ok(new ReportResponse(conferenceName, Map.of(year, map))))
                .onErrorResume(Exception.class, err -> Mono.just(ResponseEntity.badRequest().body(new ErrorResponse(err.getMessage()))));
    }

    private Mono<ResponseEntity<Object>> handleRequest(final String conferenceName,
                                                       final Function<Report, Collection<String>> reportConverter) {
        return countInfoByYear(reportService.findByConference(conferenceName)
                        /* ATTENTION: in this case Set consists only 1 element */
                        .groupBy(report -> report.getConferences().iterator().next().getYear()),
                reportConverter)
                .map(map -> new ReportResponse(conferenceName, map))
                .<ResponseEntity<Object>>map(ResponseEntity::ok)
                .onErrorResume(Exception.class, err -> Mono.just(ResponseEntity.badRequest().body(new ErrorResponse(err.getMessage()))));
    }

    private Mono<ResponseEntity<Object>> handleRequest(final Optional<Integer> year,
                                                       final Function<Report, Collection<String>> reportConverter) {
        return reportService.findAll()
                .flatMap(report -> Flux.fromIterable(report.getConferences())
                        .filter(conference -> year.isEmpty() || year.get().equals(conference.getYear()))
                        .zipWith(Mono.just(report)))
                .groupBy(t -> t.getT1().getName())
                .flatMap(group -> countInfoByYear(group.groupBy(t -> t.getT1().getYear(), Tuple2::getT2), reportConverter)
                        .map(map -> new ReportResponse(group.key(), map)))
                .collectList()
                .<ResponseEntity<Object>>map(ResponseEntity::ok)
                .onErrorResume(Exception.class, err -> Mono.just(ResponseEntity.badRequest().body(new ErrorResponse(err.getMessage()))));
    }

    private static Mono<Map<String, Long>> countInfo(final Flux<Report> reports,
                                                     final Function<Report, Collection<String>> reportConvertor) {
        return reports.flatMapIterable(report -> Objects.requireNonNullElse(reportConvertor.apply(report), Collections.emptySet()))
                .groupBy(s -> s)
                .flatMap(group -> Mono.zip(Mono.just(Objects.requireNonNull(group.key())), group.count()))
                .collectMap(Tuple2::getT1, Tuple2::getT2);
    }

    private static Mono<Map<Integer, Map<String, Long>>> countInfoByYear(final Flux<GroupedFlux<Integer, Report>> reports,
                                                                         final Function<Report, Collection<String>> reportConverter) {
        return reports.flatMap(group -> Mono.zip(Mono.just(Objects.requireNonNull(group.key())), countInfo(group, reportConverter)))
                .collectMap(Tuple2::getT1, Tuple2::getT2);
    }

    private static Set<String> languageToSetConverter(final Report report) {
        return Collections.singleton(report.getLanguage());
    }

    private static void logRequest(String path, String parameters) {
        log.info(CONTROLLER_MARKER, String.format("GET %s/%s path: %s, with params: %s", REST_API_PATH, "/report", path, parameters));
    }
    private static void logError(final Throwable e) {
        log.error(CONTROLLER_MARKER, "ERROR is happen: ", e);
    }
}
