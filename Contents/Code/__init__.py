PREFIX = '/video/xhamster'
TITLE = 'xHamster'
BASE_URL = 'http://xhamster.com'
CHANNEL_LIST = 'http://xhamster.com/channels.php'
CTYPES = ['Straight Categories','Transsexual Categories','Gay Categories']

##########################################################################################
def Start():
	ObjectContainer.title1 = TITLE
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:23.0) Gecko/20100101 Firefox/23.0'
	HTTP.CacheTime = 0

##########################################################################################
@handler(PREFIX, TITLE, thumb='icon-default.png')
def MainMenu():
	oc = ObjectContainer()
	
	oc.add(DirectoryObject(key = Callback(GetNewContent), title="Newest Videos"))
	oc.add(DirectoryObject(key = Callback(ChannelTypes), title="Categories"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/rankings/weekly-top-videos.html', pTitle=String.Quote("Top Videos - Last 7 days")), title = "Top Videos - Last 7 days"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/rankings/monthly-top-videos.html', pTitle=String.Quote("Top Videos - Last 30 days")), title = "Top Videos - Last 30 days"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/rankings/alltime-top-videos.html', pTitle=String.Quote("Top Videos - All Time")), title = "Top Videos - All Time"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/rankings/weekly-top-viewed.html', pTitle=String.Quote("Most Viewed Videos - Last 7 days")), title = "Most Viewed Videos - Last 7 days"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/rankings/monthly-top-viewed.html', pTitle=String.Quote("Most Viewed Videos - Last 30 days")), title = "Most Viewed Videos - Last 30 days"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/rankings/alltime-top-viewed.html', pTitle=String.Quote("Most Viewed Videos - All Time")), title = "Most Viewed Videos - All Time"))

	
	return oc


##########################################################################################
@route(PREFIX + '/GetNewContent')
def GetNewContent():
	return ParseVideos(BASE_URL,"Newest Videos")


##########################################################################################
@route(PREFIX + '/ParseVideos')
def ParseVideos(pURL,pTitle):
	oc = ObjectContainer(title2=pTitle)
	
	# Fugly hack - the framework doesn't seem to handle decoding a colon properly ( : )
	# so let's just rip them out and put them back as required be forcing all URLs to be relative
	# and manually putting back the full path each time
	if not pURL.startswith('http'):
		pURL = BASE_URL + pURL
	else:
		pURL = BASE_URL + pURL.split("xhamster.com")[-1]

	for video in HTML.ElementFromURL(pURL).xpath('//div[@class="video"]'):
		title = video.xpath('.//u/text()')[0]
		url = video.xpath('.//a/@href')[0]
		thumb = video.xpath('.//img/@src')[0]
		oc.add(VideoClipObject(url=url,title=title,thumb=thumb))

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
	for channel in HTML.ElementFromURL(CHANNEL_LIST).xpath("//div[contains(@class,'boxC')]//div[contains(@class,'list')][%s]//a[@class='btnBig']" % (c + 1)):
		url = channel.xpath("./@href")[0]
		title = channel.xpath("./text()")[-1].strip()
 		Log.Debug("title: " + title)
 		Log.Debug("url: " + url)
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

	# get channel name .. i.e. new-chanellname-1.html becomes channelname
	channel=pURL.split("-")[1]

	Log.Debug("Channel: "+channel)

	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/channels/new-'+channel+'-1.html', pTitle=String.Quote(pTitle + " - Latest Videos (All)")), title = "Latest Videos (All)"))
	# only show this option if it's not HD videos
	if not channel=="hd_video":
		oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/channels/hd-'+channel+'-1.html', pTitle=String.Quote(pTitle + " - Latest Videos (All)")), title = "Latest Videos (HD Only)"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/channels/top-weekly-'+channel+'-1.html', pTitle=String.Quote(pTitle + " - Latest Videos (All)")), title = "Top Videos - Last 7 Days"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/channels/top-monthly-'+channel+'-1.html', pTitle=String.Quote(pTitle + " - Latest Videos (All)")), title = "Top Videos - Last 30 Days"))
	oc.add(DirectoryObject(key = Callback(ParseVideos, pURL='/channels/top-alltime-'+channel+'-1.html', pTitle=String.Quote(pTitle + " - Latest Videos (All)")), title = "Top Videos - All Time"))

	return oc














