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
            print("questions_to_insert : ", questions_to_insert)
            # Update job document with questions
            job_collection.update_one(
                {"_id": ObjectId(job_id)},
                {"$push": {"questions": {"$each": questions_to_insert}}}
            )
            print("job.questions", job["questions"])
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

@csrf_exempt    
def answer(request, job_id, talent_id, question_id):
    if request.method == 'POST':
        try:
            # Extract answer data from request
            # print(request.body)
            # answer_data = request.POST.get('answer_data')
            # print("answer_data : ", answer_data)

            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)
            answer_data = body_data.get('answer_data')
            print("answer_data:", answer_data)
            if not answer_data:
                return HttpResponse("Answer not provided", status=400)

            # Connect to MongoDB
            client = MongoClient("mongodb://uptime:Basketball10@134.122.18.134:27017/dev_highpo?authSource=admin&w=1&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
            db = client["dev_highpo"]
            job_collection = db['jobs']

            talent_id_object = ObjectId(talent_id)
            question_id_object = ObjectId(question_id)
            job_id_object = ObjectId(job_id)


            #get the question object
            job = job_collection.find_one({"_id": job_id_object})
            # Ensure job exists
            if not job:
                return HttpResponse("Job not found", status=404)
            print("This is the job recieved : ", job["_id"])
            job_questions = job['questions']
            print("This is the job questions recieved : ", job_questions)

            # Find the job question with matching _id
            matching_question = None
            for question in job_questions:
                if question['_id'] == question_id_object:
                    matching_question = question
                    break

            if matching_question:
                print("Matching job question:" + question_id+ " : ", matching_question)
            else:
                print("No matching job question found.")

            new_answer_object = matching_question
            new_answer_object["answer"] = answer_data
            print('-------------------------new_answer_object----------------------------------')
            print("new_answer_object : ", new_answer_object)
            # new_answer_object is to be added in the application 
            print('-----------------------------------------------------------')
            job_applications = job["applications"]
            print("job_applications length : ", len(job_applications))

            # this line has to be removed later and find application dynamically
            # talent_id_object = ObjectId('63c14ae6cc828858cc653760')
            # Find the application with matching talentId
            # matching_application = None
            # for application in job_applications:
            #     if application['talentId'] == talent_id_object:
            #         matching_application = application
            #         break

            # if matching_application:
            #     print("Matching application : ", matching_application['_id'])
            # else:
            #     print("No matching application found.")
            
            # get matching application index 
            # matching_application_index = None
            # for index, application in enumerate(job['applications']):
            #     if application['talentId'] == talent_id_object:
            #         matching_application_index = index
            #         break

            # Find the matching application
            matching_application_index = None
            for index, application in enumerate(job_applications):
                if application['talentId'] == talent_id_object:
                    matching_application_index = index
                    break
            print("matching_application_index : ", matching_application_index)

            if matching_application_index is not None:
                # Check if 'job_questions' field exists in the matching application
                if 'job_questions_answers' not in job['applications'][matching_application_index]:
                    # If 'job_questions_answers' doesn't exist, create it as an empty list
                    job['applications'][matching_application_index]['job_questions_answers'] = []
                # Add the new answer object to the 'job_questions_answers' array within the matching application
                
                
                # job['applications'][matching_application_index]['job_questions_answers'].append(new_answer_object)

                # # Update the job document in the database with the modified 'applications' array
                # job_collection.update_one(
                #     {"_id": job_id_object},
                #     {"$set": {"applications": job['applications']}}
                # )
                    # Check if an object with the same _id already exists in 'job_questions' array
                existing_object_index = None
                for index, obj in enumerate(job['applications'][matching_application_index]['job_questions_answers']):
                    if obj['_id'] == new_answer_object['_id']:
                        existing_object_index = index
                        break

                if existing_object_index is not None:
                    # Update the answer of the existing object with the same _id
                    print("Question answered with this index already exists, so I will just update the answer.")
                    job['applications'][matching_application_index]['job_questions_answers'][existing_object_index]['answer'] = new_answer_object['answer']
                else:
                    # Append the new answer object to the 'job_questions_answers' array
                    job['applications'][matching_application_index]['job_questions_answers'].append(new_answer_object)

                # Update the job document in the database with the modified 'applications' array
                job_collection.update_one(
                    {"_id": job_id_object},
                    {"$set": {"applications": job['applications']}}
                )

                print("New answer object added to the matching application and job updated successfully.")
                return JsonResponse({"message": "Answer added successfully"}, status=200)
            else:
                print("No matching application found.")
                return JsonResponse({"error": "Some error occurred"}, status=400)

                # return HttpResponse("No matching application found.")

            # if matching_application_index is not None:
            #     # Add the new answer object to the job_questions array within the matching application
            #     print("ye dekh bhai : ", job['applications'][matching_application_index]['job_questions'])
            #     print("iske andar aya hu")
            #     job['applications'][matching_application_index]['job_questions'].append(new_answer_object)
            #     # Update the job document in the database with the modified job.applications array
            #     job_collection.update_one(
            #         {"_id": job_id_object},
            #         {"$set": {"applications": job['applications']}}
            #     )

            #     print("New answer object added to the matching application and job updated successfully.")
            #     return JsonResponse({"message": "Answer added successfully", "data" : job['applications'][matching_application_index]}, status=200)
            #     # return HttpResponse("Answer added successfully")
            # else:
            #     print("No matching application found.")
            #     return JsonResponse({"error": "Some error occurred"}, status=400)
                # return HttpResponse("No matching application found.")



            # Update the corresponding question with the answer
            # job_collection.update_one(
            #     {"talent._id": talent_id_object, "questions._id": question_id_object},
            #     {"$set": {"questions.$.answer": answer_data}}
            # )
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
