#!/bin/bash

sudo rm -rf drupal
tar -xf ~/Downloads/drupal-7.43.tar.gz
mv drupal-7.43 drupal
cd drupal/sites/all/modules
tar -xf ~/Downloads/civicrm-4.7.2-drupal.tar.gz
cd ../../../..
chmod u+w drupal/sites/default
sudo chown www-data:www-data -R drupal
