#!/bin/bash
sudo docker build -t tg_epic_bot .
sudo docker run -d -v /home/ec2-user/tg_epic_bot/db:/app/db --name=tg_epic_bot tg_epic_bot:latest