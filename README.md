# Deploy an out of the box MeiliSearch in DigitalOcean

### Disclaimer

The current DigitalOcean image is not yet available in the marketplace.  
This steps are only addressed for MeiliSearch team (for now).  

# Create an out of the box MeiliSearch

### 1. Create a new droplet

In any DigitalOcean page, when you are logged in, you will find a menu in the upper-right corner. Click on Create -> Droplets

![img](./doc/img/01.create.png "Create droplet")  

### 2. Select MeiliSearch snapshot

By default DigitalOcean will show you the "distributions" tab. Select the "Snapshots" tab and look for our own MeiliSearch Debian image

![img](./doc/img/02.snapshot.png "Snapshot")  

### 3. Click on show all plans

By default, Digital Ocean propose plans that might be to expensive for our testing purposes. If you want to select the cheapest plan for testing, click on "show all plans" (bottom-right corner)

![img](./doc/img/03.show-plans.png "Show all plans")  

### 4. Select your plan

Select the cheapest plan by clicking on it

![img](./doc/img/04.select-plan.png "Select plan")  

### 5. Select a region for your droplet

Select the region where you want to deploy your droplet. Remember, closer is faster, but prices can change significantly. We will choose London for this example, but it works anywhere

![img](./doc/img/05.select-region.png "Select region")  

### 6. Add your ssh key

Select your SSH key in order to be able to connect to your droplet later. If you don't see your SSH key add yours to your account.  

If you need help with this, visit [this link](https://www.digitalocean.com/docs/droplets/how-to/add-ssh-keys/to-account/)

![img](./doc/img/06.add-ssh-key.png "Add ssh key")  

### 7. Type your droplet name

Here you can select the name that will be visible everywhere in DigitalOcean account. Choose wisely!

![img](./doc/img/07.droplet-name.png "Droplet name")  

### 8. Add tags

Tags are a very good method to know who created ressources, and for organizing or cleaning purposes. Try to always add some tags so other people can know who uses the machine, and for what purposes.

![img](./doc/img/08.add-tags.png "Add tags")  

### 9. Finally click on Create Droplet

![img](./doc/img/09.create-droplet.png "Create droplet")  

### 10. Your MeiliSearch is running (with no config).  

 While creating...  

![img](./doc/img/10.creating.png "Creating") 

When it's done...  

![img](./doc/img/10.created-ip.png "Created") 

### 11. Test MeiliSearch.

Copy the public IP address

![img](./doc/img/11.copy-ip.png "Copy IP")  

Paste it in your browser. If this screen is shown, your MeiliSearch is now ready!

![img](./doc/img/11.test-meili.png "Test MeiliSearch")  


# Configure settings in your MeiliSearch Droplet

Configuring your MeiliSearch from a DigitalOcean droplet is very straigth-forward. Establish an SSH connexion with your droplet and a script will guide you through the process.

### 12. Make your domain name point to your droplet

If you want to use your own domnain name (or sub-domain), add an A record in your domain name provider account

![img](./doc/img/12.domain-a-record.png "Domain to  MeiliSearch")  

This should work out of the box. Your domain should be usable for your MeiliSearch

![img](./doc/img/12.working-domain.png "Domain to  MeiliSearch")  

### 13. Set API KEY and SSL (HTTPS)

Meilisearch is running out of the box. It means that you haven't set an API KEY (anyone can read/write from your MeiliSearch) and you can't use HTTPS. But no worries, the configuration process is automated and very simple. Just connect via SSH to your new MeiliSearch Droplet and answer a few questions:

### 13.1. Open a terminal

Open a terminal and start a new SSH connection with the IP you got from DigitalOcean  

Write in your terminal `ssh root@134.122.99.185`  and press Enter to establish connection 

![img](./doc/img/13.open-terminal-ssh.png "Terminal ssh")  

Write `yes` and press Enter to accept the authentication process  

![img](./doc/img/13.auth-yes.png "Auth")  

A script will run automatically, asking for your settings. If you want to run this script anytime, you can run it again by typing:  

`sh /var/opt/meilisearch/scripts/first-login/001-first-login.sh`

### 14. Enjoy your ready to use MeiliSearch 

Enjoy!

![img](./doc/img/14.finish.png "Enjoy")  