from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .mongo_client import get_db_handle
from datetime import datetime
from bson import ObjectId

@api_view(['GET'])
def get_tenants(request):
    db, client = get_db_handle()
    if db is None: return Response({"error": "डेटाबेस कनेक्शन अयशस्वी झाले"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        tenants = list(db['tenants'].find({}, {'name': 1, '_id': 0}))
        tenant_names = [tenant['name'] for tenant in tenants]
        return Response(tenant_names)
    finally:
        if client: client.close()

@api_view(['GET'])
def rent_status(request, tenant_name):
    db, client = get_db_handle()
    if db is None: return Response({"error": "डेटाबेस कनेक्शन अयशस्वी झाले"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        rent_details = list(db['rents'].find({'tenant_name': tenant_name}).sort('date', -1))
        for item in rent_details: item['_id'] = str(item['_id'])
        return Response(rent_details)
    finally:
        if client: client.close()

@api_view(['POST'])
def add_rent(request):
    db, client = get_db_handle()
    if db is None: return Response({"error": "डेटाबेस कनेक्शन अयशस्वी झाले"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        data = request.data
        tenant_name = data['tenant_name']
        rents_collection = db['rents']

        rents_collection.insert_one({
            'tenant_name': tenant_name,
            'amount': float(data['amount']),
            'date': datetime.now()
        })

        rent_count = rents_collection.count_documents({'tenant_name': tenant_name})

        if rent_count > 10:
            oldest_rent = rents_collection.find_one(
                {'tenant_name': tenant_name},
                sort=[('date', 1)]
            )
            if oldest_rent:
                rents_collection.delete_one({'_id': oldest_rent['_id']})

        return Response({"message": "भाडे यशस्वीरित्या जोडले गेले."}, status=status.HTTP_201_CREATED)
    finally:
        if client: client.close()

@api_view(['POST'])
def add_tenant(request):
    db, client = get_db_handle()
    if db is None: return Response({"error": "डेटाबेस कनेक्शन अयशस्वी झाले"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        data = request.data
        if db['tenants'].find_one({'name': data['name']}):
            return Response({"error": "या नावाचा भाडेकरू आधीपासून अस्तित्वात आहे."}, status=status.HTTP_400_BAD_REQUEST)
        db['tenants'].insert_one({'name': data['name'], 'joining_date': datetime.strptime(data['joining_date'], '%Y-%m-%d')})
        return Response({"message": "नवीन भाडेकरू यशस्वीरित्या जोडला गेला."}, status=status.HTTP_201_CREATED)
    finally:
        if client: client.close()

@api_view(['DELETE'])
def remove_tenant(request, tenant_name):
    db, client = get_db_handle()
    if db is None: return Response({"error": "डेटाबेस कनेक्शन अयशस्वी झाले"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        tenant_result = db['tenants'].delete_one({'name': tenant_name})
        if tenant_result.deleted_count == 0:
            return Response({"error": "भाडेकरू सापडला नाही."}, status=status.HTTP_404_NOT_FOUND)
        db['rents'].delete_many({'tenant_name': tenant_name})
        return Response({"message": f"भाडेकरू '{tenant_name}' आणि त्यांचे सर्व भाड्याचे रेकॉर्ड काढले गेले आहेत."})
    finally:
        if client: client.close()