# Small DiscordBot for temporary Voicechannels  
  
This is a small Discord Bot written in Python to handle TempChannels  
  
  
# Installation with docker  
1. setup datebase:  
  
		docker pull postgres:14  
		docker run --name name-of-db -p 5432:5432 -e POSTGRES_PASSWORD=SECRET_PW -d postgres:142. 
2. create tables:  
  
       CREATE TABLE IF NOT EXISTS public.dc_server  
		(
		guild_id text COLLATE pg_catalog."default" NOT NULL,  
		cat_id text COLLATE pg_catalog."default" NOT NULL, 
		vc_one_id text COLLATE pg_catalog."default" NOT NULL, 
		admin_role text COLLATE pg_catalog."default", 
		CONSTRAINT dc_server_pkey PRIMARY KEY (guild_id) 
		)
3. download git repository   
4. change db username, pw, and host  
5. run docker container with the TempChannelBot  

		docker build -t name-of-bot:1.0 .  
		docker run -d name-of-bot:1.0    
## Commands  
  
| Command | description |  
|--|--|  
| [prefix]setup | Setup the Tempchannel and write in Database |  
| [prefix]reset | delete tupel from Database and Delete all Tempchannels if exists |
| [prefix]admin @role| Set role to admin for bot (only server admin can use that command) | 