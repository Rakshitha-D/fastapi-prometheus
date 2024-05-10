import time
from fastapi import FastAPI, HTTPException, Request, Response,status
from datetime import datetime
from .database import connection
from .datasetmodel import UpdateDataset,Dataset
import json
import prometheus_client
app = FastAPI()

api_requests = prometheus_client.Counter("api_requests_total", "Number of API calls",["api","status"])
api_request_size = prometheus_client.Gauge("api_request_size_bytes","Request size of API call in bytes",["api","status"])
api_response_size = prometheus_client.Gauge("api_response_size_bytes","Response size of API call in bytes",["api","status"])
api_response_duration = prometheus_client.Gauge("api_response_duration_seconds","Response time of api calls",["api","status"])

def handle_response(api,response, status_code, request, start_time):
    response_json = json.dumps(response, default=str)
    response_obj = Response(content=response_json)
    response_time = time.time() - start_time

    api_requests.labels(api=api, status=status_code).inc()
    api_request_size.labels(api=api, status=status_code).inc(int(request.headers.get('content-length', 0)))
    api_response_size.labels(api=api, status=status_code).inc(len(response_json.encode('utf-8')) + len(str(response_obj.headers)))
    api_response_duration.labels(api=api, status=status_code).inc(response_time)


def get_dataset_id(dataset_id)->bool:
    connection.cursor.execute("""SELECT * from datasets where dataset_id = %s """,(dataset_id,))
    if connection.cursor.fetchone() is not None:
        return True
    return False

@app.get("/v1/dataset/{dataset_id}")
def get_dataset(dataset_id,request: Request):
    try:
        start_time = time.time()
        if get_dataset_id(dataset_id):
            connection.cursor.execute("""SELECT * FROM datasets where dataset_id = %s """,(dataset_id,))
            dataset = connection.cursor.fetchone()
            response= { "id": "api.dataset.read",
                "ver": "1.0", 
                "ts": datetime.now().isoformat() + "Z",
                "params": {
                    "err": "null",
                    "status": "successful",
                    "errmsg": "null"
                    },
                    "responseCode": "OK",
                    "result": dataset
                }
            handle_response("api.dataset.read",response, 200, request, start_time)
            return response
        else:
            response = {
            "id": "api.dataset.read",
            "ver": "1.0",
            "ts": datetime.now().isoformat() + "Z",
            "params": {
            "err": "DATASET_NOT_FOUND",
            "status": "Failed",
            "errmsg": "No dataset found with id: "+ dataset_id
            },
            "responseCode": "NOT_FOUND",
            "result": {}
            }
            handle_response("api.dataset.read",response, 404, request, start_time)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=response)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=response)
    except Exception:
        response={
            "err":"INTERNAL_SERVER_ERROR"
        }
        handle_response("api.dataset.read",response, 500, request, start_time)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/v1/dataset")
def create_dataset(dataset: Dataset,request: Request):
    try:
        start_time = time.time()
        if not get_dataset_id(dataset.dataset_id):
            updated_date = datetime.now()
            insert_fields=", ".join(f"{field}" for field in dataset.model_dump())
            insert_values = []
            for field in dataset.model_dump():
                attribute = getattr(dataset, field)
                if isinstance(attribute, dict):
                    insert_values.append(json.dumps(attribute))
                else:
                    insert_values.append(attribute)

            insert_values.append(updated_date)
            connection.cursor.execute(f"""insert into datasets ({insert_fields},updated_date) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) returning * """,insert_values)
            data=connection.cursor.fetchone()
            print(data)
            connection.conn.commit()
            response={"id": "api.dataset.create",
            "ver": "1.0",
            "ts": datetime.now().isoformat() + "Z",
            "params": {
                "err": "null",
                "status": "successful",
                "errmsg": "null"
            },
            "responseCode": "OK",
            "result": {
                "id": dataset.dataset_id,
                "data": data
            }
            }
            handle_response("api.dataset.create",response, 200, request, start_time)
            return response
        elif get_dataset_id(dataset.dataset_id):
            response = {
                "id": "api.dataset.create",
                "ver": "1.0",
                "ts": datetime.now().isoformat() + "Z",
                "params": {
                "err": "DATASET_NOT_CREATED",
                "status": "Failed",
                "errmsg": "Dataset already exists"
                },
                "responseCode": "CONFLICT",
                "result": {}
            }
            handle_response("api.dataset.create",response, 409, request, start_time)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=response)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=response)
    except Exception:
        response={
            "err":"INTERNAL_SERVER_ERROR"
        }
        handle_response("api.dataset.create",response, 500, request, start_time)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

@app.patch("/v1/dataset/{dataset_id}")
def update_dataset(dataset_id,dataset: UpdateDataset,request: Request):
    try:
        start_time = time.time()
        if get_dataset_id(dataset_id):
            update_fields = ", ".join(f"{field}=%s" for field in dataset.model_dump(exclude_unset=True))
            update_values = []
            for field in dataset.model_dump(exclude_unset=True):
                attribute = getattr(dataset, field)
                if isinstance(attribute, dict):
                    update_values.append(json.dumps(attribute))
                else:
                    update_values.append(attribute)

            updated_date= datetime.now()
            update_values.append(updated_date)
            update_values.append(dataset_id)
            connection.cursor.execute(f"""UPDATE datasets SET {update_fields},updated_date = %s WHERE dataset_id = %s RETURNING *""", update_values)
            connection.cursor.fetchone()
            connection.conn.commit()
            response={"id": "api.dataset.update",
            "ver": "1.0",
            "ts": datetime.now().isoformat() + "Z",
            "params": {
                "err": "null",
                "status": "successful",
                "errmsg": "null"
            },
            "responseCode": "OK",
            "result": {
                "id": dataset_id
            }
            }
            handle_response("api.dataset.update",response, 200, request, start_time)
            return response
        else:
            response = {
            "id": "api.dataset.update",
            "ver": "1.0",
            "ts": datetime.now().isoformat() + "Z",
            "params": {
            "err": "DATASET_NOT_FOUND",
            "status": "Failed",
            "errmsg": "No records found"
            },
            "responseCode": "NOT_FOUND",
                "result": {}
            }
            handle_response("api.dataset.update",response, 404, request, start_time)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=response)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=response)
    except Exception:
        response={
            "err":"INTERNAL_SERVER_ERROR"
        }
        handle_response("api.dataset.update",response, 500, request, start_time)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

@app.delete("/v1/dataset/{dataset_id}")
def delete_dataset(dataset_id,request: Request):
    try:
        start_time = time.time()
        if not get_dataset_id(dataset_id):
            response = {
            "id": "api.dataset.delete",
            "ver": "1.0",
            "ts": datetime.now().isoformat() + "Z",
            "params": {
            "err": "DATASET_NOT_FOUND",
            "status": "Failed",
            "errmsg": "No records found"
            },
            "responseCode": "NOT_FOUND",
            "result": {}
            }
            handle_response("api.dataset.delete",response, 404, request, start_time)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=response)
        else:
            start_time = time.time()
            connection.cursor.execute("""DELETE FROM datasets where id = %s returning *""",(dataset_id,))
            connection.cursor.fetchone()
            connection.conn.commit()
            response={"id": "api.dataset.delete",
            "ver": "1.0",
            "ts": datetime.now().isoformat() + "Z",
            "params": {
                "err": "null",
                "status": "successful",
                "errmsg": "null"
                },
            "responseCode": "OK",
            "result": {
                "id": dataset_id
                }
            }
            handle_response("api.dataset.delete",response, 200, request, start_time)
            return response
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=response)
    except Exception:
        response={
            "err":"INTERNAL_SERVER_ERROR"
        }
        handle_response("api.dataset.delete",response, 500, request, start_time)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@app.get("/metrics")
def get_metrics():
    #registry = prometheus_client.CollectorRegistry()
    #registry.register(api_requests)
    #registry.register(api_response_duration)
    #registry.register(api_request_size)
    #registry.register(api_response_size)
    #registry.register(api_response_size_sample)
    #metrics_data = prometheus_client.generate_latest(registry=registry)
    metrics_data = prometheus_client.generate_latest()
    api_response_size.clear()
    api_response_duration.clear()
    api_request_size.clear()
    return Response(
        media_type="text/plain",
        content=metrics_data)