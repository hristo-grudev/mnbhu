import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import MnbhuItem
from itemloaders.processors import TakeFirst

base = 'https://www.mnb.hu/ajax/next?id=b175665&page={}'

class MnbhuSpider(scrapy.Spider):
	name = 'mnbhu'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		data = json.loads(response.text)
		post_links = scrapy.Selector(text=data["Data"]).xpath('//div[@class="news"]')
		for post in post_links:
			date = post.xpath('./p[@class="date"]/text()').get()
			url = post.xpath('./h3/a/@href').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		if post_links:
			self.page += 1
			next_page = base.format(self.page)
			yield response.follow(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@class="border"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=MnbhuItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
