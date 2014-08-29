import facebook
import datetime
import sys

# fb = facebook.Facebook('bd100b49340effa90332cdfbe6e85659','b150ebbad9cdff51269248dbe4b9683d')
api_key = 'bd100b49340effa90332cdfbe6e85659'
secret_key = 'b150ebbad9cdff51269248dbe4b9683d'
fb = facebook.Facebook(api_key,secret_key)
stamp = datetime.datetime.now()
fb.fbml.setRefHandle('myhandle','Last Updated at %s'%stamp)
sys.exit(0)


fb.auth.createToken()
fb.login()
print "Press Enter When logged in."
sys.stdin.readline()  # sleep(100)

session = fb.auth.getSession()
print session


print "Get User Info"
print fb.users.getInfo([fb.uid], ['name', 'birthday'])

print "Setting Profile Info:"
fb.profile.setFBML('',fb.uid,'Box','','','Wall and Info')

