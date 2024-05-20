from django.shortcuts import render,HttpResponse
from pymongo import MongoClient
from bson import ObjectId
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pymongo import mongo_client
import json

def test(request):
    return HttpResponse('Testing completed!')

@csrf_exempt
def create_question(request, job_id):
    if request.method == 'POST':
        try:
            # Extract job questions from request
            data = json.loads(request.body)
            job_questions = data.get('questions', [])

            if not job_questions:
                return JsonResponse({"error": "No questions provided"}, status=400)

            # Connect to MongoDB
            client = MongoClient("mongodb://uptime:Basketball10@134.122.18.134:27017/dev_highpo?authSource=admin&w=1&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
            db = client["dev_highpo"]
            job_collection = db['jobs']

            # Convert job_id to ObjectId
            job_id_object = ObjectId(job_id)

            # Fetch the job document
            job = job_collection.find_one({"_id": job_id_object})

            # Check if job is not None
            if job is None:
                return JsonResponse({"error": "Job not found"}, status=404)

            # Prepare questions to insert
            questions_to_insert = []
            for question_data in job_questions:
                question_id = ObjectId()
                question = {
                    "_id": question_id,
                    "question": question_data.get("question"),
                    "isRequired": question_data.get("isRequired", False)  # Default to False if not provided
                }
                questions_to_insert.append(question)

            # Update job document with questions
            job_collection.update_one(
                {"_id": ObjectId(job_id)},
                {"$push": {"questions": {"$each": questions_to_insert}}}
            )

            return JsonResponse({"message": "Questions added successfully"})
        
        except Exception as error:
            return JsonResponse({"error": str(error)}, status=500)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

def show_all_questions(request,job_id):
    if request.method == "GET":
        try:
            client = MongoClient("mongodb://uptime:Basketball10@134.122.18.134:27017/dev_highpo?authSource=admin&w=1&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
            db = client["dev_highpo"]
            job_collection = db['jobs']

            job_id_object = ObjectId(job_id)

            # Fetch the job document
            job = job_collection.find_one({"_id": job_id_object})
            print(job)
            # Check if job is not None
            if job is None:
                return HttpResponse("Job not found")
            
            else:
                return HttpResponse(job['questions'])

        except Exception as error:
            return HttpResponse(str(error))
    else:
        return HttpResponse("Only get request is allowed")
    
def answer(request, talent_id, question_id):
    if request.method == 'POST':
        try:
            # Extract answer data from request
            answer_data = request.POST.get('answer_data')
            if not answer_data:
                return HttpResponse("Answer not provided", status=400)

            # Connect to MongoDB
            client = MongoClient("mongodb://uptime:Basketball10@134.122.18.134:27017/dev_highpo?authSource=admin&w=1&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
            db = client["dev_highpo"]
            job_collection = db['jobs']

            talent_id_object = ObjectId(talent_id)
            question_id_object = ObjectId(question_id)

            # Update the corresponding question with the answer
            job_collection.update_one(
                {"talent._id": talent_id_object, "questions._id": question_id_object},
                {"$set": {"questions.$.answer": answer_data}}
            )

            return HttpResponse("Answer added successfully")

        except Exception as error:
            return HttpResponse(str(error), status=500)

    else:
        return HttpResponse("Only POST requests are allowed", status=405)

# from django.shortcuts import render,HttpResponse
# from pymongo import MongoClient
# from bson import ObjectId
# from django.views.decorators.csrf import csrf_exempt
# from pymongo import mongo_client

# def test(request):
#     return HttpResponse('Testing completed!')

# @csrf_exempt
# def create_question(request,job_id):
#     print(request.body)
#     if request.method == 'POST':
#         try:
#             # Extract date of completing assignment from request
#             question_data = request.POST.get('question_data')
#             if not question_data:
#                 return HttpResponse("Question not provided", status=400)

#             # Connect to MongoDB
#             client = MongoClient("mongodb://uptime:Basketball10@134.122.18.134:27017/dev_highpo?authSource=admin&w=1&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
#             db = client["dev_highpo"]
#             job_collection = db['jobs']

#             # Convert job_id to ObjectId
#             job_id_object = ObjectId(job_id)

#             # Fetch the job document
#             job = job_collection.find_one({"_id": job_id_object})

#             # Check if job is not None
#             if job is None:
#                 return HttpResponse("Job not found", status=404)

#             question_id = ObjectId()

#                 # Update talent document with assignment information
#             job_collection.update_one(
#                     {"_id": ObjectId(job_id)},
#                     {"$push": {"questions": {"_id": question_id, "question": question_data}}}
#                 )

#             return HttpResponse("Question added successfully")
        
#         except Exception as error:
#             return HttpResponse(str(error), status=500)
    
#     else:
#         return HttpResponse("Only POST requests are allowed", status=405)


# def show_all_questions(request, job_id):
#     if request.method == "GET":
#         try:
#             client = MongoClient("mongodb://uptime:Basketball10@134.122.18.134:27017/dev_highpo?authSource=admin&w=1&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
#             db = client["dev_highpo"]
#             job_collection = db['jobs']

#             job_id_object = ObjectId(job_id)

#             # Fetch the job document
#             job = job_collection.find_one({"_id": job_id_object})
#             print(job)
#             # Check if job is not None
#             if job is None:
#                 return HttpResponse("Job not found")
            
#             else:
#                 return HttpResponse(job['questions'])

#         except Exception as error:
#             return HttpResponse(str(error))
#     else:
#         return HttpResponse("Only get request is allowed")
    
# def answer(request, talent_id, question_id):
#     if request.method == 'POST':
#         try:
#             # Extract answer data from request
#             answer_data = request.POST.get('answer_data')
#             if not answer_data:
#                 return HttpResponse("Answer not provided", status=400)

#             # Connect to MongoDB
#             client = MongoClient("mongodb://uptime:Basketball10@134.122.18.134:27017/dev_highpo?authSource=admin&w=1&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
#             db = client["dev_highpo"]
#             job_collection = db['jobs']

#             talent_id_object = ObjectId(talent_id)
#             question_id_object = ObjectId(question_id)

#             # Update the corresponding question with the answer
#             job_collection.update_one(
#                 {"talent._id": talent_id_object, "questions._id": question_id_object},
#                 {"$set": {"questions.$.answer": answer_data}}
#             )

#             return HttpResponse("Answer added successfully")

#         except Exception as error:
#             return HttpResponse(str(error), status=500)

#     else:
#         return HttpResponse("Only POST requests are allowed", status=405)
