from django.shortcuts import render,HttpResponse
from pymongo import MongoClient
from bson import ObjectId
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import datetime
from django.http import JsonResponse
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

def test(request):
    return HttpResponse('Testing completed!')

@csrf_exempt
def create_assignment(request, job_id):
    if request.method == 'POST':
        try:
            file_data = request.FILES.get('file')
            title = request.POST.get('title')
            description = request.POST.get('description')
            completion_date_str = request.POST.get('due_date') 
            print(file_data, title, description, completion_date_str)
            if not (title or description or completion_date_str or file_data): 
                return HttpResponse("Title or description or completion_date_str not given. File is not compulsary", status=400)

            completion_date = datetime.strptime(completion_date_str, '%Y-%m-%d')  
            print("completion_date", completion_date)
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )

            assignment_creation_time = datetime.now()
            client = MongoClient("mongodb://uptime:Basketball10@134.122.18.134:27017/dev_highpo?authSource=admin&w=1&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
            db = client["dev_highpo"]
            job_collection = db['jobs']

            # Convert job_id to ObjectId
            job_id_object = ObjectId(job_id)
            print("job_collection", job_collection)

            # Fetch the job document
            job = job_collection.find_one({"_id": job_id_object})
            # Upload file to S3
            key = f'{job_id}/{file_data.name}'
            s3.upload_fileobj(file_data, settings.AWS_S3_BUCKET_NAME, key)
            s3_url = f'https://{settings.AWS_S3_BUCKET_NAME}.s3.ap-south-1.amazonaws.com/{key}'

            # Update MongoDB document with S3 URL
            # s3_url = f'https://{settings.AWS_S3_BUCKET_NAME}.s3.ap-south-1.amazonaws.com/{key}'
            assignment_data = {
                "title":title,
                "filename": file_data.name,
                "s3_url": s3_url,
                "description":description,
                "completion_date": completion_date, 
                "assignment_creation_time":assignment_creation_time
            }
            
            job_collection.update_one(
                {"_id": job_id_object},
                {"$set": {"assignment": assignment_data}}
            )
            return HttpResponse("Assignment uploaded successfully")
        except ClientError as e:
            return HttpResponse(str(e), status=500)
    else:
        return HttpResponse("Only POST requests are allowed", status=405)


# @csrf_exempt
# def create_assignment(request, job_id):
#     if request.method == 'POST':
#         try:
#             file_data = request.FILES.get('file')
#             title = request.POST.get('title')
#             description = request.POST.get('description')
#             completion_date_str = request.POST.get('due_date') 
#             print(file_data, title, description, completion_date_str)
#             if not (title or description or completion_date_str): 
#                 return HttpResponse("Title or description or completion_date_str not given. File is not compulsary", status=400)

#             completion_date = datetime.strptime(completion_date_str, '%Y-%m-%d')  
#             print("completion_date", completion_date)
#             s3 = boto3.client(
#                 's3',
#                 aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#                 aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#                 region_name=settings.AWS_REGION
#             )

#             assignment_creation_time = datetime.now()
#             client = MongoClient("mongodb://uptime:Basketball10@134.122.18.134:27017/dev_highpo?authSource=admin&w=1&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
#             db = client["dev_highpo"]
#             job_collection = db['jobs']

#             # Convert job_id to ObjectId
#             job_id_object = ObjectId(job_id)
#             print("job_collection", job_collection)

#             s3_url=''
#             # Fetch the job document
#             if file_data:
#                 job = job_collection.find_one({"_id": job_id_object})
#                 # Upload file to S3
#                 key = f'{job_id}/{file_data.name}'
#                 s3.upload_fileobj(file_data, settings.AWS_S3_BUCKET_NAME, key)
#                 s3_url_local = f'https://{settings.AWS_S3_BUCKET_NAME}.s3.ap-south-1.amazonaws.com/{key}'
#                 s3_url = s3_url_local

#             # Update MongoDB document with S3 URL
#             # s3_url = f'https://{settings.AWS_S3_BUCKET_NAME}.s3.ap-south-1.amazonaws.com/{key}'
#             assignment_data = {
#                 "title":title,
#                 "filename": file_data.name if file_data else '',
#                 "s3_url": s3_url if file_data else '',
#                 "description":description,
#                 "completion_date": completion_date, 
#                 "assignment_creation_time":assignment_creation_time
#             }
            
#             job_collection.update_one(
#                 {"_id": job_id_object},
#                 {"$set": {"assignment": assignment_data}}
#             )
#             return HttpResponse("Assignment uploaded successfully")
#         except ClientError as e:
#             return HttpResponse(str(e), status=500)
#     else:
#         return HttpResponse("Only POST requests are allowed", status=405)


# @csrf_exempt
# def assign_all(request, job_id):
#     if request.method == 'POST':
#         try:
#             client = MongoClient("mongodb://uptime:Basketball10@134.122.18.134:27017/dev_highpo?authSource=admin&w=1&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
#             db = client["dev_highpo"]
#             job_collection = db['jobcandidatematchings']
#             talent_collection = db['talents']

#             # Convert job_id to ObjectId
#             job_id_object = ObjectId(job_id)

#             assignment_job = db['jobs'].find_one({"_id": ObjectId(job_id)})
#             if not assignment_job or "assignment" not in assignment_job:
#                 return HttpResponse("Assignment data not found for this job", status=404)

#             assignment_data = assignment_job["assignment"]
#             completion_date = assignment_data.get("completion_date")
#             job = job_collection.find_one({"_id": job_id_object})

#             if job is None:
#                 return HttpResponse("Job not found", status=404)

#             # Iterate over matchedTalents array
#             for talent_info in job.get("matchedTalents", []):
#                 talent_id = talent_info.get("talentId")
#                 assignment_data = {
#                     "job_id": job_id, 
#                     "assignment_data":assignment_job["assignment"],
#                     "completion_date": completion_date,
#                 }

#                 talent_collection.update_one(
#                     {"_id": ObjectId(talent_id)},
#                     {"$push": {"assignment": assignment_data}}
#                 )

#             return HttpResponse("Assignments assigned successfully")
        
#         except Exception as error:
#             return HttpResponse(str(error), status=500)
    
#     else:
#         return HttpResponse("Only POST requests are allowed", status=405)

@csrf_exempt 
def assign_all(request, talent_type, job_id):
    if request.method == 'POST':
        try:
            print("run test")
            client = MongoClient("mongodb://uptime:Basketball10@134.122.18.134:27017/dev_highpo?authSource=admin&w=1&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
            db = client["dev_highpo"]
            job_collection = db['jobs']
            talent_collection = db['talents']
            # Convert job_id to ObjectId
            job_id_object = ObjectId(job_id)
            assignment_job = db['jobs'].find_one({"_id": job_id_object})
            job = job_collection.find_one({"_id": job_id_object})
            if job is None:
                return HttpResponse("Job not found", status=404)
            print('job found : ', job["_id"])
            if not assignment_job or "assignment" not in assignment_job:
                return HttpResponse("Assignment data not found for this job || Create assignment first", status=404)
            assignment_data = assignment_job["assignment"]
            print("assignment_data found", assignment_data)
            # completion_date = assignment_data[0].get("completion_date") if assignment_data else None
            completion_date = assignment_data.get("completion_date") if assignment_data else None
            # Filter talents based on talent_type
            talents_to_assign = []
            for application in job["applications"]:
                talent_id = application["talentId"]
                if talent_type in application and application.get(talent_type, True):
                    talent = talent_collection.find_one({"_id": ObjectId(talent_id)})
                    if talent:
                        talents_to_assign.append(talent)
            talents_to_assign = []
            for application in job["applications"]:
                if isinstance(application, dict):
                    talent_id = application.get("talentId")
                    if talent_id and talent_type in application and application.get(talent_type, True):
                        talent = talent_collection.find_one({"_id": ObjectId(talent_id)})
                        if talent:
                            talents_to_assign.append(talent)
            # Assign the job to filtered talents
            for talent in talents_to_assign:
                assignment_data = {
                    "job_id": job_id,
                    "assignment_data": assignment_job["assignment"],
                    "completion_date": completion_date,
                }
                # assignment_data = {
                #     "title":title,
                #     "filename": file_data.name,
                #     "s3_url": s3_url,
                #     "description":description,
                #     "completion_date": completion_date, 
                #     "assignment_creation_time":assignment_creation_time
                # }
                talent_collection.update_one(
                    {"_id": talent["_id"]},
                    {"$push": {"assignment": assignment_data}}
                )
            return HttpResponse("Assignment assigned successfully")
        except Exception as error:
            print("Error in assign_all : ", error)
            return HttpResponse(str(error), status=500)
    else:
        return HttpResponse("Only POST requests are allowed", status=405)

@csrf_exempt
def assign_to_talent(request, talent_id,job_id):
    if request.method == 'POST':
        try:
            client = MongoClient("mongodb://uptime:Basketball10@134.122.18.134:27017/dev_highpo?authSource=admin&w=1&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
            db = client["dev_highpo"]
            talent_collection = db['talents']
            assignment_job = db['jobs'].find_one({"_id": ObjectId(job_id)})
            if not assignment_job or "assignment" not in assignment_job:
                return HttpResponse("Assignment data not found for this job", status=404)
            assignment_data = assignment_job["assignment"]
            completion_date = assignment_data.get("completion_date")
            # Check if the talent exists
            talent = talent_collection.find_one({"_id": ObjectId(talent_id)})
            if talent is None:
                return HttpResponse("Talent not found", status=404)
            # Create assignment data
            assignment_data = {
                "job_id": job_id,
                "assignment_data": assignment_job["assignment"],
                "completion_date": completion_date,
                "assigned_date" : datetime.now()
            }
            # Update talent document with assignment data
            talent_collection.update_one(
                {"_id": ObjectId(talent_id)},
                {"$push": {"assignment": assignment_data}}
            )
            return HttpResponse("Assignment assigned successfully")
        except Exception as error:
            return HttpResponse(str(error), status=500)
    else:
        return HttpResponse("Only POST requests are allowed", status=405)

@csrf_exempt
def submit(request, job_id, talent_id):
    if request.method == 'POST':
        try:
            # Connect to MongoDB
            client = MongoClient("mongodb://uptime:Basketball10@134.122.18.134:27017/dev_highpo?authSource=admin&w=1&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
            db = client["dev_highpo"]
            talent_collection = db['talents']
            talent_id_object = ObjectId(talent_id)
            job_id_object = ObjectId(job_id)
            current_date = datetime.now()
            # Get the talent document
            talent = talent_collection.find_one({"_id": talent_id_object})
            if talent is None:
                return HttpResponse("Talent not found", status=404)
            # Check if there's a completion date for the specific job_id
            job_assignment = None
            for assignment in talent.get("assignment", []):
                if assignment.get("job_id") == str(job_id_object):
                    job_assignment = assignment
                    break
            if job_assignment is None:
                return HttpResponse("Assignment for this job not found for the talent", status=404)
            # Check if the current date is after the completion date
            completion_date = job_assignment.get("completion_date")
            late_submission = current_date > completion_date
            # Upload solution to S3
            solution = request.FILES.get('solution')
            description = request.POST.get('description')
            if not solution:
                return HttpResponse("No solution of assignment uploaded", status=400)
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            key = f'{talent_id}/{solution.name}'
            s3.upload_fileobj(solution, settings.AWS_S3_BUCKET_NAME, key)
            # Update MongoDB document with S3 URL and late_submission flag
            s3_url = f'https://{settings.AWS_S3_BUCKET_NAME}.s3.ap-south-1.amazonaws.com/{key}'
            talent_collection.update_one(
                {"_id": talent_id_object, "assignment.job_id": str(job_id_object)},
                {"$set": {
                    "assignment.$.assignment_solution_url": s3_url,
                    "assignment.$.late_submission": late_submission,
                    "assignment.$.description": description,
                    "assignment.$.upload_date": current_date,
                }}
            )
            return HttpResponse("Solution uploaded successfully")
        except Exception as error:
            return HttpResponse(str(error), status=500)
    else:
        return HttpResponse("Only POST requests are allowed", status=405)
# def submit(request, talent_id):
#     if request.method == 'POST':
#         try:
#             # Connect to MongoDB
#             client = MongoClient("mongodb://uptime:Basketball10@134.122.18.134:27017/dev_highpo?authSource=admin&w=1&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
#             db = client["dev_highpo"]
#             talent_collection = db['talents']
            
#             talent_id_object = ObjectId(talent_id)
#             current_date = datetime.now()

#             # Get the talent document
#             talent = talent_collection.find_one({"_id": talent_id_object})
#             if talent is None:
#                 return HttpResponse("Talent not found", status=404)

#             # Check if there's a completion date
#             completion_date = talent.get("assignment", {}).get("completion_date")

#             # Check if the current date is after the completion date
#             late_submission = current_date > completion_date

#             # Upload solution to S3
#             solution = request.FILES.get('solution')
#             if not solution:
#                 return HttpResponse("No solution of assignment uploaded", status=400)

#             s3 = boto3.client(
#                 's3',
#                 aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#                 aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#                 region_name=settings.AWS_REGION
#             )
#             key = f'{talent_id}/{solution.name}'
#             s3.upload_fileobj(solution, settings.AWS_S3_BUCKET_NAME, key)

#             # Update MongoDB document with S3 URL and late_submission flag
#             s3_url = f'https://{settings.AWS_S3_BUCKET_NAME}.s3.ap-south-1.amazonaws.com/{key}'
#             talent_collection.update_one(
#                 {"_id": talent_id_object},
#                 {"$set": {
#                     "assignment_solution_url": s3_url,
#                     "late_submission": late_submission
#                 }}
#             )
#             return HttpResponse("Solution uploaded successfully")
#         except Exception as error:
#             return HttpResponse(str(error), status=500)
#     else:
#         return HttpResponse("Only POST requests are allowed", status=405)





# def show_assignment(request, job_id):
#     try:
#         # Connect to MongoDB
#         client = MongoClient("mongodb://uptime:Basketball10@134.122.18.134:27017/dev_highpo?authSource=admin&w=1&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
#         db = client["dev_highpo"]
#         job_collection = db['jobs']

#         # Convert job_id to ObjectId
#         job_id_object = ObjectId(job_id)

#         # Fetch the job document
#         job = job_collection.find_one({"_id": job_id_object})

#         # Check if job is not None
#         if job is not None and "assignment" in job:
#             assignment_data = job["assignment"]
#             filename = assignment_data.get("filename", "")
#             s3_url = assignment_data.get("s3_url", "")
#             if filename and s3_url:
#                 return JsonResponse({"assignment_data":assignment_data})
#             else:
#                 return HttpResponse("Filename or s3_url not found in assignment data", status=400)
#         else:
#             return HttpResponse("Job not found", status=404)

#     except Exception as error:
#         return HttpResponse(str(error), status=500)