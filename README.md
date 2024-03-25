# Storage System

## Installation

1. Create environment:
    ```
    python -m venv .venv
    ```

2. Activate environment:
    ```
    .venv\Scripts\activate
    ```

3. Install requirements:
    ```
    pip install -r requirements.txt
    ```

#### Create Database

1. Create a mysql with MySQL workbench or other ways

2. Create a `secrets.json` at `code/data`

3. Add secret information
Example:
```
{   
    "username": "root",
    "password": "root",
    "db_name": "storagesystem",
    "test_db_name": "test_storagesystem",
    "hostname": "localhost"
}
```
#### Install Front-end React requirements
1. Install Node.js
    [https://nodejs.org](https://nodejs.org)

2. npm install at app location

Go to
```
code/react/storage-app
```
Run
```
npm install
```
Might have to run
```
npm audit fix --force
```


## Run API and Front-end

1. Launch API service at main.py location

Go to
```
code/
```
Run
```
uvicorn main:app --reload
```
Launch browser
```
localhost:8000/docs
```

2. Lauch React Front-end at App location

Go to
```
code/react/storage-app 
```
Run
```
npm start
```
Launch browser
```
localhost:3000
```

## Run Tests

Go to
```
code/
```
Run
```
python -m unittest -v test_async.py
```

## Specificaftions

##### Basic requirements
Status | Requirement
:---:| ---

##### Advanced requirements
Status | Requirement
:---:| ---

##### Misc requirements
Status | Requirement
:---:| ---

## Diagrams