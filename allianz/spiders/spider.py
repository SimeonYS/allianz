import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import AllianzItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class AllianzSpider(scrapy.Spider):
	name = 'allianz'
	start_urls = ['https://www.allianz.bg/bg_BG/individuals/press-center.result.html/1.html',
				  'https://www.allianz.bg/bg_BG/individuals/articles-center.html'
				  ]

	def parse(self, response):
		post_links = response.xpath('//a[@class="c-link c-link--block u-margin-bottom-lg"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="c-link c-pagination-compact__next js-articleindex-navigation"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):

		date = response.xpath('//div[@class="c-copy   c-stage__additional-info  u-text-hyphen-auto"]/div[@style="text-align: center;"]//text()').get()
		if not date:
			date = "Blog"
		title = ' '.join(response.xpath('//h1[contains(@class,"c-heading  c-heading--page")]//text()|//h2[contains(@class,"u-text-hyphen-none")]//text() | //h1[contains(@class,"c-heading  c-heading--page c-heading--page c-stage__headline c-link--capitalize u-text-hyphen-none")]/p//text()').getall()).strip()
		title = title.replace('\xa0',' ')
		if not title:
			title = ' '.join(response.xpath('//span[@class="c-breadcrumb__link is-active"]//text()').getall()).strip()
		content = response.xpath('//div[@class="l-container l-container--full-width t-bg-"]//div[@class="text"]//text()|//span[contains(@class,"c-heading  c-heading--subsection-medium")]//text() |//div[@class="c-copy     u-text-hyphen-manual"]//text()|//div[@class="c-copy     u-text-hyphen-manual"]//text()').getall()
		content = [p.strip() for p in content if p.strip()][:-1]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=AllianzItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
