### About

This repo manages the code for https://rabbithole223.com/

A push to main will build the site and deploy, currently notifying joshua.miller@fitsnips.net of build inits and errors. 


Upon push to the staging branch a build will be deployed to https://staging.rabbithole223.amplifyapp.com/ the user name is "admin" and the password is in 1password.

The git repo lives at https://github.com/rabbithole223/web-rabbithole223.com and is owned by rabbithole223 user.


AWS applify link

https://us-east-1.console.aws.amazon.com/amplify/home?region=us-east-1#/d1odx3yxd5kea7

AWS account_id 427662681066, username in 1password is joshua.miller+aws@fitsnips.net





### Install hugo with Brew on OSX

```
web-rabbithole223.com on  staging [!?] on 🅰 (va) 
🕙[ Aug/25/23 - 19:59:55 ] ❯ brew install hugo 
==> Downloading https://formulae.brew.sh/api/formula.jws.json
##################################################################################################################################### 100.0%
==> Downloading https://formulae.brew.sh/api/cask.jws.json
##################################################################################################################################### 100.0%
Warning: hugo 0.117.0 is already installed and up-to-date.
To reinstall 0.117.0, run:
  brew reinstall hugo
```



### Add new content 

hugo new content posts/<page_name>.md


example:

```
hugo new content posts/about.md
```


### Get content ready to server, not just staged

run the command hugo, which will put the rendered pages in public folder

```
web-rabbithole223.com on  staging [!?] on 🅰 (va) 
🕙[ Aug/25/23 - 19:59:54 ] ❯ hugo 
Start building sites … 
hugo v0.117.0-b2f0696cad918fb61420a6aff173eb36662b406e+extended darwin/amd64 BuildDate=2023-08-07T12:49:48Z VendorInfo=brew


                   | EN  
-------------------+-----
  Pages            | 11  
  Paginator pages  |  0  
  Non-page files   |  0  
  Static files     |  1  
  Processed images |  0  
  Aliases          |  1  
  Sitemaps         |  1  
  Cleaned          |  0  

Total in 87 ms
```


### Validate the env config 

Env configs are in config/<env_name>.toml

you can dump the config locally with the config command

hugo config --environment <env_name> 

For example if I was to check the value of title in staging env

```
web-rabbithole223.com on  staging [!] on 🅰 (va) 
🕙[ Aug/26/23 - 11:51:22 ] ❯ hugo config --environment staging |grep title
pluralizelisttitles = true
title = 'Open Mind Fabricators Staging'
titlecasestyle = 'AP'
        title = true
  subtitle = 'Knowledge Through Experimentation'
```


Images can be pushed to s3://static-origin.rabbithole223.com/images/ and be used in a post using the cloudfront url

```
![Hydroponic Humidifier System](https://static.rabbithole223.com/images/mwgk-humi-hydro01.jpeg)

```