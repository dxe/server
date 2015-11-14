#Health Endpoint
[The health endpoint](http://dxetech.org/health) gives a quick look into
whether or not things on the server are broken. By looking here, you can see
with a pretty high level of confidence (medium level precision) whether or
not things are working.

##Monitoring
[Uptime Robot](https://uptimerobot.com/) hits this endpoint every 5 minutes and
does a string match for all the Success strings. If it can't find the string
(meaning something is broken), it sends an email to our error email alias to
notify us.

##Adding New Health Info
If you're adding something to the server, you should add some representation of
it to the health endpoint. Figure out some way to programattically test if it's
working or not. This could be hitting an endpoint or web page you made to see if
it returns with a 200 status code and has the kind of data you expect, or
verifying that a file was updated recently, or a file was uploaded recently.
Add it to [the health endpoint](health.py) with a human readable description of
how you know it's working or in what way it's not working.

Then you need to add a new keyword monitor to Uptime Robot to check for your
success string.
