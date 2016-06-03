Forking & Syncing
=================

* Fork pytube/antioch.git to YOUR_USERNAME using https://github.com/pytube/antioch#fork-destination-box
* Clone YOUR_USERNAME/antioch.git
```sh
git clone git@github.com:YOUR_USERNAME/antioch.git
```

* Configure upstream repository 
```sh
git remote add upstream https://github.com/pytube/antioch.git
```

* To sync your fork with upstream
```sh
git fetch upstream
git checkout master
git merge upstream/master
```

Development Environment with Docker
===================================

* build

```sh
docker-compose build
```


Running Tests
=============

```sh
docker-compose run antioch-tests
```
