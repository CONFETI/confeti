import re

import scrapy
from confeti_scraper.items import ConferenceInfo, Reports, Speakers, ContactInfo
from scrapy.http import Request

class JpointSpider(scrapy.Spider):
    name = 'jpoint2019_scraper'
    allowed_domains = ['jpoint.ru']
    start_urls = ['http://2019.jpoint.ru/en']

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
        self.conference['name'] = 'Jpoint'
        self.conference['year'] = response.xpath('//h2[@class="hero-info_date"]/text()').get().strip()[-4::]
        self.conference['location'] = 'Moscow'
        self.conference['url'] = response.url
        self.conference['logo'] = ''
        self.next_page = ''.join((response.url,'/#schedule'))
        return Request(self.next_page, callback=self.parse_reports)

    def parse_reports(self, response):
        for frame in response.xpath('//div[re:test(@class,"schedule__cell schedule__cell--talk col-\d-\d-\d")]'):
            report_dict={}
            material_links=[]
            try:
                report_link = ''.join(('https://2019.jpoint.ru',frame.xpath('.//a[@class="link schedule__link"]/@href').get(),'/'))
                complexity_text = frame.xpath('.//div[@class="schedule__helper"]//img/@title').get()
                if complexity_text is not None:
                    report_dict['complexity'] = {'value':self.COMPLEXITY_VALUES[complexity_text], 'description':complexity_text}
                report_dict['language'] = frame.xpath('.//span[@class="schedule__talk-lang "]/text()').get().strip()
                report_dict['tags'] = [tag.strip()[1::] for tag in frame.xpath('.//i[@class="schedule__tags"]//nobr/text()').getall()]
                yield Request(
                                report_link,
                                callback=self.parse_authors,
                                meta={'report_dict':report_dict}
                             )
            except TypeError as typeErr:
                print(f'raised {typeErr}')

    def parse_authors(self, response):
        report = Reports()
        try:
            report['complexity'] = response.meta['report_dict']['complexity']
        except KeyError:
            pass
        report['language'] = response.meta['report_dict']['language']
        report['tags'] = response.meta['report_dict']['tags']
        report['title'] = response.xpath('//h1[@class="talk_title"]/text()').get()
        speakers_list=[]
        for speaker_sec in response.xpath('//div[@class="talk-speaker"]'):
            speaker = Speakers()
            contact_info = ContactInfo()
            speaker['name'] = speaker_sec.xpath('.//h5[@class="speaker-info_name"]/text()').get().strip()
            speaker['avatar'] = ''.join(('https:',speaker_sec.xpath('.//img[@class="img-fluid"]/@src').get()))
            company_name = speaker_sec.xpath('.//h6[@class="speaker-info_company"]/text()').get()
            if company_name is not None:
                contact_info['company'] = {'name':company_name,'year':int(self.conference['year'])}
            twitter_name = speaker_sec.xpath('.//div[@class="speaker_profiles"]//a[@class="twitter_link"]/@href').get()
            if twitter_name is not None:
                contact_info['twitterUsername'] = twitter_name
            speaker['contactInfo']=contact_info
            speakers_list.append(speaker)
        report['speakers'] = speakers_list
        self.conference['report'] = report
        yield self.conference
        