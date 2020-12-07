package org.confeti.controllers.dto.core;

import lombok.Data;
import lombok.experimental.Accessors;

import java.util.Map;
import java.util.UUID;

@Accessors(chain = true)
@Data
public class SpeakerStatResponseByYear {
    private UUID id;
    private Map<Integer, Long> years;
}
