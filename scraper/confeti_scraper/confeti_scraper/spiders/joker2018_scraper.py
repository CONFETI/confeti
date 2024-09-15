import re

import scrapy
from confeti_scraper.items import ConferenceInfo, Reports, Speakers, ContactInfo
from scrapy.http import Request

class Joker2018ScraperSpider(scrapy.Spider):
    name = 'joker2018_scraper'
    allowed_domains = ['jokerconf.com']
    start_urls = ['https://2018.jokerconf.com/en']

    def __init__(self):
        self.COMPLEXITY_VALUES ={
                                  'Get ready, will burn':0,
                                  'Introduction to technology':1,
                                  'For practicing engineers':2,
                                  "Hardcore. Really hard and demanding talk, you'll understand only if you're an experienced engineer.":3
                                }

        self.conference = ConferenceInfo()
        self.next_page = ''

    def parse(self, response):
        date_and_location = [i.strip() for i in response.xpath('//span[@class="hero__info "]/text()').getall()]
        self.conference['year'] = date_and_location[0]
        self.conference['location'] = 'Saint-Petersburg'
        self.conference['logo'] = ''.join((response.url[:-4],response.xpath('//a[@class="header__logo"]//img/@src').get()))
        self.conference['url'] = response.url
        self.conference['name'] = 'Joker'
        self.next_page=''.join((response.url,'#schedule'))
        return Request(self.next_page, callback=self.parse_reports)

    def parse_reports(self, response):
        for frame in response.xpath('//div[re:test(@class,"pt-col-talk schedule__talk col-\d-\d-\d")]'):
            report_dict = {}
            material_links = []
            try:
                report_link=''.join(('https://2018.jokerconf.com', frame.xpath('.//a[@class="event_talk_link"]/@href').get(),'/'))
                if ('bof' in frame.xpath('.//a[@class="event_talk_link"]//strong/text()').get().lower()) \
                    or ('party' in frame.xpath('.//a[@class="event_talk_link"]//strong/text()').get().lower()):
                    continue
                report_dict['tags'] = [tag.strip()[1::] for tag in frame.xpath('.//span[@class="tags"]//nobr/text()').getall()]
                complexity_text = frame.xpath('.//span[@class="rating_icon"]//img/@title').get()
                if complexity_text is not None:
                    report_dict['complexity'] = {'value':self.COMPLEXITY_VALUES[complexity_text], 'description':complexity_text}
                report_dict['language'] = frame.xpath('.//span[@class="cell-lang"]/text()').get().strip()
                yield Request(
                    report_link,
                    callback=self.parse_authors,
                    meta={'report_dict': report_dict}
                )
            except TypeError as type_err:
                print(f'raised {type_err}')
                continue

    def parse_authors(self, response):
        report = Reports()
        try:
            report['complexity'] = response.meta['report_dict']['complexity']
        except KeyError:
            oass
        report['language'] = response.meta['report_dict']['language']
        report['tags'] = response.meta['report_dict']['tags']
        report['title'] = response.xpath('//h1[@class="talk_title"]/text()').get().strip()
        speakers_list=[]
        for speaker_sec in response.xpath('//div[@class="talk-speaker"]'):
            speaker = Speakers()
            contact_info = ContactInfo()
            speaker['name'] = speaker_sec.xpath('.//h5[@class="speaker-info_name"]/text()').get().strip()
            speaker['avatar'] = ''.join(('https:',speaker_sec.xpath('.//img[@class="img-fluid"]/@src').get()))
            company_name = speaker_sec.xpath('.//h6[@class="speaker-info_company"]/text()').get()
            if company_name is not None:
                contact_info['company'] = {'name':company_name,'year':2018}
            twitter_name = speaker_sec.xpath('.//div[@class="speaker_profiles"]//a[@class="twitter_link"]/@href').get()
            if twitter_name is not None:
                contact_info['twitterUsername'] = twitter_name 
            speaker['contactInfo']=contact_info
            speakers_list.append(speaker)
        report['speakers'] = speakers_list
        self.conference['report'] = report
        yield self.conference
        