# Приложение YaMDb c REST API
[![ci/cd](https://github.com/Talpik/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)](https://github.com/Talpik/yamdb_final/actions/workflows/yamdb_workflow.yml)
* Приложение YaMDb с умеет собирать отзывы пользователей на произведения. 
* Произведения можно разделить на различные категории (например: Фильмы, Игры, Музыка, Книги). 
* Произведению может быть присвоен жанр из созданного списка (например: Фантастика, Рок, Стратегии). 
* Новые жанры может создавать только администратор. 
* Благодарные или возмущённые читатели оставляют к произведениям текстовые отзывы и выставляют произведению рейтинг (от 1 до 10). 
* Из множества оценок автоматически высчитывается средняя оценка произведения.
* Потестировать `http://84.252.136.27/api/v1/`
## Запуск приложения
1. Создайте рабочую директорию для хранения проекта:
<br> `mkdir ~/Dev`
2. Склонируйте репозиторий на ваш компьютер:
<br> `git clone https://github.com/Talpik/infra_sp2.git ~/Dev/yamdb`
3. Установите Docker для запуска приложения:
<br> <https://docs.docker.com/engine/install/>
4. Перейдите в папку проекта **yamdb**:
<br> `cd ~/Dev/yambd`
5. Запустите утилиту **docker-compose**, чтобы развернуть контейнеры:
<br> `docker-compose up`
6. Проверьте запущенные контейнеры:
<br> `docker container ls` и скопируйте занчение **CONTAINER ID** контейнера **web**
7. Проведите миграции внутри контейнера **web**:
<br> `docker exec -it <container id> python manage.py migrate`
8. Создайте суперпользователя:
<br> `docker exec -it <container id> python manage.py createsuperuser` *(email явлвется обязательным - по нему осуществляется доступ в админку)*
9. Заполните базу начальными данными из подготовленного файла *fixtures.json*:
<br> `docker exec -it <container id> python loaddata fixtures.json`
## Настройка доступных хостов
Настройка доступных хостов осуществляется в файле *.env*:
<br> `ALLOWED_HOSTS=84.252.136.27,localhost`
<br> Через запятую можно добавлять другие значения.
## Основные точки доступа
1. Админка:          <br>`84.252.136.27/admin`
2. API v1.0:         <br>`127.0.0.1/api/v1`
3. Все произведения: <br>`84.252.136.27/api/v1/titles`
4. Все жанры:        <br>`84.252.136.27/api/v1/genres`
5. Все пользователи: <br>`84.252.136.27/api/v1/users` (нужен токен авторизации)
6. Все категории:    <br>`84.252.136.27/api/v1/categories`
7. Все отзывы:       <br>`84.252.136.27/api/v1/titles/<titile_id>/reviews/` (где <titile_id> - целое числа)
8. Все комментарии:  <br>`84.252.136.27/api/v1/titles/<titile_id>/reviews/<reviews_id>/comments` (где <titile_id> и <reviews_id> - целые числа)
