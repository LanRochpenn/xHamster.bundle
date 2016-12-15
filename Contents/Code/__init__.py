PREFIX = '/video/xhamster'
TITLE = 'xHamster'
BASE_URL = 'http://xhamster.com'
CHANNEL_LIST = ['http://xhamster.com/channels.php','http://xhamster.com/channels-shemale','http://xhamster.com/channels-gay'];
CTYPES = ['Straight Categories','Transsexual Categories','Gay Categories']
ICON='icon-default.png'

##########################################################################################
def Start():
	ObjectContainer.title1 = TITLE
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:23.0) Gecko/20100101 Firefox/23.0'
	HTTP.CacheTime = 2
	DirectoryObject.thumb = R(ICON)
	InputDirectoryObject.thumb = R(ICON)
	VideoClipObject.thumb = R(ICON)

##########################################################################################
@handler(PREFIX, TITLE, thumb=ICON)
def MainMenu():
	oc = ObjectContainer()
	
	oc.add(DirectoryObject(key = Callback(GetNewContent), title="Newest Videos"))
	oc.add(DirectoryObject(key = Callback(ChannelTypes), title="Categories"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/rankings/daily-top-videos.html', pTitle=String.Quote("Top Videos - Today")), title = "Top Videos - Today"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/rankings/weekly-top-videos.html', pTitle=String.Quote("Top Videos - Last 7 days")), title = "Top Videos - Last 7 days"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/rankings/monthly-top-videos.html', pTitle=String.Quote("Top Videos - Last 30 days")), title = "Top Videos - Last 30 days"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/rankings/alltime-top-videos.html', pTitle=String.Quote("Top Videos - All Time")), title = "Top Videos - All Time"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/rankings/weekly-top-viewed.html', pTitle=String.Quote("Most Viewed Videos - Last 7 days")), title = "Most Viewed Videos - Last 7 days"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/rankings/monthly-top-viewed.html', pTitle=String.Quote("Most Viewed Videos - Last 30 days")), title = "Most Viewed Videos - Last 30 days"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/rankings/alltime-top-viewed.html', pTitle=String.Quote("Most Viewed Videos - All Time")), title = "Most Viewed Videos - All Time"))
	oc.add(InputDirectoryObject(key = Callback(Search), title = 'Search Videos', prompt = 'Search Videos'))	
	
	return oc


##########################################################################################
@route(PREFIX + '/GetNewContent')
def GetNewContent():
	return ParseVideos(BASE_URL,"Newest Videos")


##########################################################################################
@route(PREFIX + '/ParseVideos')
def ParseVideos(pURL,pTitle):
	oc = ObjectContainer(title2=pTitle)
	
	# Fugly hack - we can end up with three kinds of URLs here
	# http://xhamster.com/blah.html OR /blah.html OR blah.html 
	# so deal with that accordingly, also
	# the framework doesn't seem to handle decoding a colon properly ( : )
	# so let's just rip them out and put them back as required be forcing all URLs to be relative
	# and manually putting back the full path each time

	# force an Unquote to be safe
	pURL = String.Unquote(pURL)

	# not a full pathed relative url?  i.e. search.php?q=test .. make it so, i.e. /search.php?q=test
	if not pURL.startswith('http') and not pURL.startswith('/'):
		pURL = '/' + pURL
	
	# not an absolute url?  If so make it one
	if not pURL.startswith('http'):
		pURL = BASE_URL + pURL
	else:
		# this was a passed absolute url, likely with a broken : so split and recreate with the proper base
		pURL = BASE_URL + pURL.split("xhamster.com")[-1]

	try:
		for video in HTML.ElementFromURL(pURL).xpath("//div[contains(@class,'video')]"):
			title = video.xpath('.//u/text()')[0]
			url = video.xpath('.//a/@href')[0]
			thumb = video.xpath('.//img/@src')[0]
			# no clients display this in regular listings any longer
			#rating = float(video.xpath('.//div[@class="fr"]/text()')[0].strip('%'))/10

			try:
				duration = Datetime.MillisecondsFromString(video.xpath('.//b/text()')[0])
			except:
				duration = 0

			oc.add(VideoClipObject(url=url,title=title,duration=duration,thumb=thumb))
	except:
		# nothing was found
		NoResults=""
		Log.Debug("No Results Found!")
		
	# next page object?
 	try:
		nextURL = HTML.ElementFromURL(pURL).xpath("//div[contains(@class,'pager')]//a[contains(@class,'last')]/@href")[0]
		oc.add(NextPageObject(key=Callback(ParseVideos, pURL=String.Quote(nextURL), pTitle=String.Quote(pTitle)), title="More ..."))
 	except:
		# do nothing
 		nextURL = ""

	return oc


##########################################################################################
@route(PREFIX + '/GetChannels', c=int)
def GetChannels(c):
	oc = ObjectContainer()
	for channel in HTML.ElementFromURL(CHANNEL_LIST[c]).xpath("//div[contains(@class,'letter-categories')]//a"):
		url = channel.xpath("./@href")[0]
		title = channel.xpath("./text()")[-1].strip()
		oc.add(DirectoryObject(key = Callback(ChannelOptions, pURL=String.Quote(url), pTitle=String.Quote(title)), title=title))
		
	oc.objects.sort(key = lambda obj: obj.title, reverse=False)		
	return oc


##########################################################################################
@route(PREFIX + '/ChannelTypes')
def ChannelTypes():
	oc = ObjectContainer(title2="Select Channel Type")

	oc.add(DirectoryObject(key = Callback(GetChannels, c=int(0)), title=CTYPES[0]))
	oc.add(DirectoryObject(key = Callback(GetChannels, c=int(1)), title=CTYPES[1]))
	oc.add(DirectoryObject(key = Callback(GetChannels, c=int(2)), title=CTYPES[2]))

	return oc
	
##########################################################################################
@route(PREFIX + '/ChannelOptions')
def ChannelOptions(pURL,pTitle):
	oc = ObjectContainer(title2="Select Channel Option")

	# strip to relative URL only
	pURL = pURL.split("xhamster.com")[-1]

	# get channel name .. i.e. new-chanelname-1.html becomes channelname
	channel=pURL.split("-")[1]

	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/channels/new-'+channel+'-1.html', pTitle=String.Quote(pTitle + " - Latest Videos (All)")), title = "Latest Videos (All)"))
	# only show this option if it's not HD videos
	if not channel=="hd_videos":
		oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/channels/hd-'+channel+'-1.html', pTitle=String.Quote(pTitle + " - Latest Videos (All)")), title = "Latest Videos (HD Only)"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/channels/top-daily-'+channel+'-1.html', pTitle=String.Quote(pTitle + " - Latest Videos (All)")), title = "Top Videos - Today"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/channels/top-weekly-'+channel+'-1.html', pTitle=String.Quote(pTitle + " - Latest Videos (All)")), title = "Top Videos - Last 7 Days"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/channels/top-monthly-'+channel+'-1.html', pTitle=String.Quote(pTitle + " - Latest Videos (All)")), title = "Top Videos - Last 30 Days"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/channels/top-alltime-'+channel+'-1.html', pTitle=String.Quote(pTitle + " - Latest Videos (All)")), title = "Top Videos - All Time"))

	return oc

@route(PREFIX + '/Search')
####################################################################################################
# We add a default query string purely so that it is easier to be tested by the automated channel tester
def Search(query="test"):
	search=String.Quote(query, usePlus=True)
	return ParseVideos(pURL="/search.php?new=&q=%s&qcat=video" % search, pTitle="Search xHamster")


