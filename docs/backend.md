Backend is the FastAPI server that takes the frame and apply processing and detection on it, then it save the data locally to provide a realtime status for our js dashboard.


To run the server
```cmd
uvicorn main:app --reload
```
> --reload allows restarting the server when you modify the server files, to test it directly. Note that as per FastAPI docs, it is being used only for development but not the production.  

You can also specify the host and the port. 
```cmd
uvicorn main:app --port 8000 --host 0.0.0.0
```

Last but not least, you can select number of workers here
```cmd
uvicorn main:app --port 8000 --host 0.0.0.0 --workers 1
```

You can use `/docs` -> http://127.0.0.1:8000/docs  to check and test the server manually. or Even `/redoc` both are really useful. 

And now lets move to WebSockets, It is like a phone call, you send and get data back and forth. It provides two way communication not like HTTP which is request-response only. 
* https://fastapi.tiangolo.com/advanced/websockets/#try-it

This one was great, checked many stuff like pydantic with WebSocket. 

Previously i used to create and store a bunch of trackers per camera and store results in a database, but for now it is not like this. everything is really real time, if i have a camera that i am getting frames from, i create an instance and cache them, if the camera or dashboard disconnected, the instances being removed. 

I had a question, is app.state shared per router only? 
No it is shared on the whole fastapi server. 

Also there is a file called `health` in routes, this file is so simple but important, it is being used to know and make sure if the server is still live. 
* https://fastapi.tiangolo.com/tutorial/bigger-applications/#import-apirouter 


I faced some issues in the logger, As mentioned as suggested, i wanted to create yaml for confings, and override with .evn when needed. but it didn't wark as expected. 
until i checked this one -> 
* https://stackoverflow.com/questions/79719460/how-to-use-yaml-file-parameter-for-pydantic-settings
* This also helped alot => https://github.com/pydantic/pydantic-settings/issues/259


regarding loggging, there is also a great tool called PROMETHEUS, it is used side by side with loggers (struct log), it is being used to collect data, and numbers to show and draw them later via an endpoint. 
prometheus works on, you export these data into /metrics http endpoint, and he scrap and show them not in real time, but everytime you refresh it. 

the most important thig of this for now, is that really i confirmed that i have an issue with my prallel camera code, only one of them is working, not all together.

for profiling, cProfile is not suggested, as it lacks handling async.
py-spy, scalence, pyinstrument is suggested. 

if you faced any conflics using conda, do this. 
```bash
# To check if it is in conda
conda search package_name

# Installing the package using channel conda-forge, and update others to meet the requirements and fix conflicts. 
conda insatll package_name -c conda-forge --update-all
```


We used `app.state` to manage storages between pages, but this only works on one worker, so if you run this project on more than one worker, it is going to crash, The solution here is to use `redis`


also i have a great question, how this data is going to be fetched, and i have two answers, per floor or per camera, 
the per camera selection is going to be really hard, as it is going to be many number of fetching, as it is per camera, and also it is going to be for each time you select this floor. 
So the better answer here, is per floor, you just pull the full floor details, and then you filter what you exactly need. 

For the model, It is really beign suggested to let HF handling downloading and storing the model, don't hardcode the model path or the file. 

Now we came to really critical point, which is moving to redis, but before this, i aimed to collect and monitor and profile my project, ofcourse for comparing and has a better understanding how this system works. I planeed to use MLFlow for the system, and prometheus for now.. 

as i notinced, locally websockets works fine, but for production, add the --ws flag, as locally we use `ws://` but in prod we use `wss://`