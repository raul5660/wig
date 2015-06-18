import re, json

class Output:
	def __init__(self, options, data):
		self.results = None
		self.data = data
		self.options = options

		# calc the amount of fingerprints
		fps = data['fingerprints'].data
		num_fps_js		= sum([len(fps['js'][fp_type]['fps']) for fp_type in fps['js']])
		num_fps_os		= len(fps['os']['fps'])
		num_fps_cms		= sum([len(fps['cms'][fp_type]['fps']) for fp_type in fps['cms']])
		num_fps_plat	= sum([len(fps['platform'][fp_type]['fps']) for fp_type in fps['platform']])
		num_fps_vuln	= sum([len(fps['vulnerabilities'][source]['fps']) for source in fps['vulnerabilities']])
		self.num_fps = num_fps_js + num_fps_os + num_fps_cms + num_fps_plat + num_fps_vuln

		self.sections = [
			{
				'name': 'version',
				'headers': {
					1: {'title': 'SOFTWARE', 'color': 'blue', 'bold': True},
					2: {'title': 'VERSION',  'color': 'blue', 'bold': True},
					3: {'title': 'CATEGORY',  'color': 'blue', 'bold': True}
				},
				'titles': [
					{'category': 'cms',					'title': 'CMS'},
					{'category': 'js',					'title': 'JavaScript'},
					{'category': 'platform',			'title': 'Platform'},
					{'category': 'os',					'title': 'Operating System'},
				]
			},
			{
				'name': 'vulnerabilities',
				'headers': {
					1: {'title': 'SOFTWARE',        'color': 'blue', 'bold': True},
					2: {'title': 'VULNERABILITIES', 'color': 'blue', 'bold': True},
					3: {'title': 'LINK',            'color': 'blue', 'bold': True}
				},
				'titles': [
					{'category': 'vulnerability',          'title': '%s'},
				]
			},
			{
				'name': 'tool',
				'headers': {
					1: {'title': 'TOOL',			'color': 'blue', 'bold': True},
					2: {'title': 'SOFTWARE',		'color': 'blue', 'bold': True},
					3: {'title': 'LINK',			'color': 'blue', 'bold': True}
				},
				'titles': [
					{'category': 'tool',             'title': '%s'},
				]
			},
			{
				'name': 'subdomains',
				'headers': {
					1: {'title': 'DOMAIN',			'color': 'blue', 'bold': True},
					2: {'title': 'TITLE',			'color': 'blue', 'bold': True},
					3: {'title': 'IP',				'color': 'blue', 'bold': True}
				},
				'titles': [
					{'category': 'subdomains',		'title': '%s'},
				]
			},
			{
				'name': 'interesting',
				'headers':{
					1: {'title': 'URL',				'color': 'blue', 'bold': True},
					2: {'title': 'NOTE',			'color': 'blue', 'bold': True},
					3: {'title': 'CATEGORY',		'color': 'blue', 'bold': True}
				},
				'titles': [
					{'category': 'interesting',		'title': 'Interesting URL'},
				]
			}
		]

		self.sections_names = [s['name'] for s in self.sections]
		self.ip = self.title = self.cookies = None

	def replace_version_text(self, text):
		# replace text in version output with something else
		# (most likely an emtpy string) to improve output
		text = re.sub('^wmf/', '', text)
		text = re.sub('^develsnap_', '', text)
		text = re.sub('^release_candidate_', '', text)
		text = re.sub('^release_stable_', '', text)
		text = re.sub('^release[-|_]', '', text, flags=re.IGNORECASE)	# Umbraco, phpmyadmin
		text = re.sub('^[R|r][E|e][L|l]_', '', text)				
		text = re.sub('^mt', '', text)				# Movable Type
		text = re.sub('^mybb_', '', text)			# myBB
		return text

	def find_section_index(self, section):
		index = 0
		for elm in self.sections:
			if elm['name'] == section: return index
			index += 1

		return None

	def update_stats(self):
		self.stats = {
			'runtime':		'Time: %.1f sec' % (self.data['runtime'], ),
			'url_count':	'Urls: %s' % (self.data['url_count'], ),
			'fp_count':		'Fingerprints: %s' % (self.num_fps, ),
		}

	def loop_results(self, section):
		versions = self.sections[self.find_section_index(section)]
		for item in versions['titles']:
			if item['category'] not in self.results: continue
			for software in sorted(self.results[item['category']]):
				version = self.results[item['category']][software]
				category = item['title']
				yield (category, software, version)


class OutputJSON(Output):
	def __init__(self, options, data):
		super().__init__(options, data)
		self.json_data = []
	
	def add_results(self):
		self.results = self.data['results'].results
		site_info = self.data['results'].site_info

		site = {
			'statistics': {
				'start_time': self.data['timer'],
				'run_time': self.data['runtime'],
				'urls': self.data['url_count'],
				'fingerprints': self.num_fps
			},
			'site_info': {
				'url': self.options['url'],
				'title': site_info['title'],
				'cookies': [c for c in site_info['cookies']],
				'ip': site_info['ip']
			},
			'data': []
		}

		# add versions
		for section in self.sections_names:
			tmp = ''
			for result in self.loop_results(section):
				category, software, version = result

				if section == 'vulnerabilities':
					site['data'].append({
						'category': 'vulnerability',
						'name': software[0],
						'version': software[1],
						'link': version['col3'],
						'vulnerability_count': version['col2']
					})
				elif section == 'tool':
					site['data'].append({
						'category': 'tools',
						'name': software,
						'version': version
					})					
				
				else:
					site['data'].append({
						'category': category,
						'name': software,
						'version': version
					})

		self.json_data.append(site)

	def add_error(self, msg):
		self.json_data.append({
			'site_info': {
				'url': self.options['url'],
				'error': msg
			}
		})

	def write_file(self):
		file_name = self.options['write_file']
		with open(file_name+ '.json', 'w') as fh:
			fh.write(json.dumps(self.json_data, sort_keys=True, indent=4, separators=(',', ': ')))


class OutputPrinter(Output):

	def __init__(self, options, data):
		super().__init__(options, data)
		self.col_widths =  {1: 0, 2: 0, 3: 0}


	def _set_col_1_width(self, results):
		self.col_widths[1] = 2 + max(
			max([len(i['headers'][1]['title']) for i in self.sections]),	# length of section header titles
			max([len(p) for c in results for p in results[c]] + [0]), 			# length of software name from results
			len(self.stats['runtime'])										# length of status bar (time)
		)

	def _set_col_2_width(self, results):		
		self.col_widths[2] = 2 + max(
			max([ len(i['headers'][2]['title']) for i in self.sections ]),							# length of section header titles
			max([ len(' | '.join(results[c][p])) for c in results for p in results[c] ] + [0]),	# length of version details from results
			len(self.stats['url_count'])															# length of status bar (urls)
		)
		
	def _set_col_3_width(self, results):
		self.col_widths[3] = max(
			max([len(i['title']) for s in self.sections for i in s['titles']]),	# length of titles
			len(self.stats['fp_count'])												# length of status bar (fps)
		)

	def print_results(self):
		p = self.data['printer']

		self.results = self.data['results'].get_results()
		for category in self.results:
			for name in self.results[category]:
				versions = self.results[category][name]
				if len(versions) > 5:
					msg = '... (' + str(len(versions)-5) + ')'
					self.results[category][name] = versions[:5] + [msg]

		self.update_stats()
		self._set_col_1_width(self.results)
		self._set_col_2_width(self.results)
		self._set_col_3_width(self.results)

		p.build_line('\nTITLE\n', 'blue', True)
		p.build_line(self.data['results'].site_info['title'], 'normal')
		p.print_built_line()

		if self.data['results'].site_info['cookies']:
			p.build_line('\nCOOKIES\n', 'blue', True)
			p.build_line(', '.join(list(self.data['results'].site_info['cookies'])), 'normal')
			p.print_built_line()

		p.build_line('\nIP\n', 'blue', True)
		p.build_line(self.data['results'].site_info['ip'] + '\n', 'normal')
		p.print_built_line()

		for section in self.sections_names:
			lines = []
			for result in self.loop_results(section):
				category, software, version = result
				
				col1 = ' '.join(list(software)) if type(software) == tuple else software
				col2 = [version['col2']] if 'col2' in version else version
				col3 = category % (version['col3'],) if 'col3' in version else category
						
				lines.append( (col1, col2, col3) )

			if lines:
				section_index = self.find_section_index(section)
				headers = self.sections[section_index]['headers']
				col1,col2,col3 = headers[1], headers[2], headers[3]

				p.build_line(col1['title'], col1['color'], col1['bold'])
				p.build_line(' ' * (self.col_widths[1] - len(col1['title'])), 'normal')
				p.build_line(col2['title'], col2['color'], col2['bold'])
				p.build_line(' ' * (self.col_widths[2] - len(headers[2]['title'])), 'normal')
				p.build_line(col3['title'], col3['color'], col3['bold'])
				p.print_built_line()

				for col1, col2, col3 in lines:
					p.build_line(col1 + ' ' * (self.col_widths[1] - len(col1)), 'normal')

					#col 2
					if len(col2) > 1:
						v = [self.replace_version_text(i) for i in col2]
						p.build_line(' | '.join(v) + ' ' * (self.col_widths[2] - len(' | '.join(v))), 'normal')
					else:
						v = self.replace_version_text(col2[0])
						p.build_line(v + ' ' * (self.col_widths[2] - len(v)), 'normal')

					p.build_line(col3 + '\n', 'normal')

				p.print_built_line()

		# status bar
		time = self.stats['runtime']   + ' ' * (self.col_widths[1] - len(self.stats['runtime']))
		urls = self.stats['url_count'] + ' ' * (self.col_widths[2] - len(self.stats['url_count'])) 
		fps  = self.stats['fp_count']

		p.build_line('_'*sum(self.col_widths.values())+'\n', 'blue', True)
		p.build_line(''.join([ time, urls, fps ]), 'normal')
		p.print_built_line()
