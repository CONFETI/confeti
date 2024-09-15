import re
import scrapy
from confeti_scraper.items import ConferenceInfo, Reports, Speakers, ContactInfo
from scrapy.http import Request
from confeti_scraper import materials_form

class Jbreak2018Spider(scrapy.Spider):
    name = 'jbreak2018'
    allowed_domains = ['jbreak.ru/en']
    start_urls = ['https://jbreak.ru/en/']

    def __init__(self):
        self.COMPLEXITY_VALUES ={
                                  'Get ready, will burn':0,
                                  'Introduction to technology':1,
                                  'For practicing engineers':2,
                                  "Hardcore. Really hard and demanding talk, you'll understand only if you're an experienced engineer.":3,
                                  None: -1
                                }
        self.conference = ConferenceInfo()
        self.next_page = ''

    def parse(self, response):
        self.conference['name'] = 'JBreak'
        self.conference['year'] = '2018'
        self.conference['url'] = response.url
        self.conference['location'] = response.xpath('//h2[@class="intro__subtitle"]').get().strip()[-1:-3]
        self.next_page = ''.join((response.url,'#sheduleTable'))
        return Request(self.next_page, callback=self.parse_reports)

    def parse_reports(self, response):
        for cell in response.xpath('//table[@id="sheduleTable"]'):
            for cell_content in cell.xpath('.//tr//td'):
                report_dict = {}
                material_links = []
                complexity_text = cell_content.xpath('.//div[@class="talk-legend"]//span//img/@alt').get()
                report_dict['complexity'] = {'value':self.COMPLEXITY_VALUES[complexity_text], 'name':complexity_text}
                report_dict['tags'] = []
                material_links = cell_content.xpath('.//div[@class="talk-legend"]'):
                    .append(materials_form.materials_form(material.xpath('.//a/@href').get()))
                report_dict['source'] = material_links
                report_dict['language'] = cell_content.xpath('.//div[@class="cell-lang"]/text()').get().strip()
                report_link = ''.join(('https://2018.jbreak.ru/en/', cell_content.xpath('.//a[class="event_talk_link"]/@href').get()))
                yield Request(
                            report_link,
                            callback=self.parse_authors,
                            meta = {'report_dict': report_dict}       
                         ) 

    def parse_authors(self, response):
        report = Reports()
        report['complexity'] = response.meta['report_dict']['complexity']
        report['language'] = response.meta['report_dict']['language']
        report['source'] = response.meta['report_dict']['source']
        report['tags'] = response.meta['report_dict']['tags']
        report['title'] = response.xpath('//h1[@class="page-top__title"]/text()').get().strip()
        report['description'] = response.xpath('//div[@class="container"]//p/text()').get().strip()
        speakers_list = []
        for speaker_sec in response.xpath('//div[@class="speaker-profile"]'):
            speaker = Speakers()
            contact_info = ContactInfo()
            speaker['name'] = speaker_sec.xpath('.//h4/text()').get().strip()
            speaker['avatar'] = speaker_sec.xpath('.//div[@class="speaker__photo"]//picture//img/@srcset').get()
            speaker['bio'] = speaker_sec.xpath('.//div[@class="speaker__main"]//p/text()').getall().strip()
            #contact_info['company'] = (speaker_sec.xpath('.//h6[@class="speaker-info_company"]/text()').get(), self.conference['year'])
            contact_info['twitterUsername'] =  speaker_sec.xpath('.//a[@class="socials__link social__link--tw"]/@href').get()
            speaker['contactInfo']=contact_info
            speakers_list.append(speaker)
        report['speakers'] = speakers_list
        self.conference['report'] = report
        yield self.conference

