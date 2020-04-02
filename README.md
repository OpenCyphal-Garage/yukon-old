# Yukon


| SonarCloud (master)|[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=UAVCAN_Yukon&metric=alert_status)][1]|
|--------------------|----------------------------------------------------------------------------------------------------------------------|


## Installation & Development Instructions

``` bash

# install frontend
cd frontend
npm install

# serve with hot reload at localhost:8080
npm run dev

# build for production with minification
npm run build

#install backend
cd ../backend
# install dependencies
pip install todo

# run server
python app.py
```

## Or run setup.sh

(You have to run the backend manually after)

## Discussion

Discussion takes part at the official [UAVCAN Forums](https://forum.uavcan.org/), specifically at [Yukon UI & Rest API](https://forum.uavcan.org/t/yukon-ui-rest-api/390/1) and [GUI Tool - Next Generation](https://forum.uavcan.org/t/gui-tool-next-generation/229) forum threads.

## Backend Swagger Documentation

[Swaggerhub Api Docs Link](https://app.swaggerhub.com/apis-docs/Zarkopafilis/Yukon/1.0.0)

Most up to date swagger json is located at the `SWAGGERHUB` branch, under `/spec`. [swagger.json](https://github.com/UAVCAN/Yukon/blob/SWAGGERHUB/spec/swagger.json)


[1]: https://sonarcloud.io/dashboard?id=UAVCAN_Yukon