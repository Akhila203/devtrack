from django.shortcuts import render

# Create your views here.
import json, os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Reporter, Issue, CriticalIssue, LowPriorityIssue

REPORTERS_FILE = 'reporters.json'
ISSUES_FILE = 'issues.json'

def get_data(f):
    return json.load(open(f)) if os.path.exists(f) else []

def save_data(f, d):
    with open(f, 'w') as file: json.dump(d, file, indent=4)

@csrf_exempt
def reporters_api(request):
    reporters = get_data(REPORTERS_FILE)
    if request.method == 'GET':
        rid = request.GET.get('id')
        if rid:
            res = next((r for r in reporters if r['id'] == int(rid)), None)
            return JsonResponse(res) if res else JsonResponse({'error': 'Not found'}, status=404)
        return JsonResponse(reporters, safe=False)
    
    if request.method == 'POST':
        try:
            d = json.loads(request.body)
            obj = Reporter(d['id'], d['name'], d['email'], d['team'])
            obj.validate()
            reporters.append(obj.to_dict())
            save_data(REPORTERS_FILE, reporters)
            return JsonResponse(obj.to_dict(), status=201)
        except Exception as e: return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def issues_api(request):
    issues = get_data(ISSUES_FILE)
    if request.method == 'GET':
        iid = request.GET.get('id')
        stat = request.GET.get('status')
        if iid:
            res = next((i for i in issues if i['id'] == int(iid)), None)
            return JsonResponse(res) if res else JsonResponse({'error': 'Issue not found'}, status=404)
        if stat:
            return JsonResponse([i for i in issues if i['status'] == stat], safe=False)
        return JsonResponse(issues, safe=False)

    if request.method == 'POST':
        try:
            d = json.loads(request.body)
            p = d['priority']
            args = (d['id'], d['title'], d['description'], d['status'], p, d['reporter_id'])
            
            if p == 'critical': issue = CriticalIssue(*args)
            elif p == 'low': issue = LowPriorityIssue(*args)
            else: issue = Issue(*args)

            issue.validate()
            res = issue.to_dict()
            res['message'] = issue.describe()
            issues.append(res)
            save_data(ISSUES_FILE, issues)
            return JsonResponse(res, status=201)
        except Exception as e: return JsonResponse({'error': str(e)}, status=400)
