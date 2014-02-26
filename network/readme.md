# Network Stuff

Using the `socket` library in Python!

1. *void_server* and *one_message_client*: watch with glee as the server accepts a message from the client... and prints it! 
2. *terriblechat*: being really inefficient with non-blocking sockets
3. *terminalchat*: using the `select` library to be less inefficient; handling catastrophes such as "what if a client disconnects?!"
4. *pywget*: specify a URL, and the file that it points to shall be downloaded to your current directory as you watch a report of download progress in tense anticipation

#Resources
* http://docs.python.org/3/howto/sockets.html
* http://pymotw.com/2/select/
* http://ilab.cs.byu.edu/python/
* [Book: Foundations of Python Network Programming](http://www.apress.com/9781430230038)
* https://synack.me/blog/using-python-tcp-sockets