from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
import requests

User = get_user_model()

#Auth
@method_decorator(ensure_csrf_cookie, name="dispatch")
class CSRF(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        #sets csrf cookies
        return Response({"detail" : "CSRF cookies set"})

class Register(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email", "")
        if not username or not password:
            return Response({"detail" : "username and password required"}, status=400)
        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            return Response({"detail": "User Registered Successfully"})
        except IntegrityError:
            return Response({"detail": "Username already exists please choose another username"}, status=400)

class Login(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"detail": "Invalid credentials"}, status=400)
        login(request, user)
        return Response({"username": user.username, "email": user.email})

class Logout(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        logout(request)
        return Response({"detail": "User Logged out successfully"})

class UserView(APIView):
    def get(self, request):
        u = request.user
        return Response({"authenticated": True, "username": u.username, "email": u.email})
    
class Indicators(APIView):
    """
    Query params:
      country: e.g. IN
      codes: comma-separated indicator codes (e.g. NY.GDP.MKTP.CD,SP.POP.TOTL)
      start: year (e.g. 2000)
      end: year (e.g. 2023)
    """
    def get(self, request):
        country = request.query_params.get("country", "IN")
        codes = request.query_params.get("codes", "NY.GDP.MKTP.CD,SP.POP.TOTL").split(",")
        start = request.query_params.get("start", "2000")
        end = request.query_params.get("end", "2023")

        base = "https://api.worldbank.org/v2/country/{country}/indicator/{code}?format=json&per_page=20000&date={start}:{end}"
        series = []
        for code in codes:
            url = base.format(country=country, code=code.strip(), start=start, end=end)
            r = requests.get(url, timeout=20)
            if r.status_code != 200:
                return Response({"detail":"world bank error", "code": code}, status=502)
            data = r.json()
            if not isinstance(data, list) or len(data) < 2:
                continue
            meta, points = data[0], data[1]
            name = points[0]["indicator"]["value"] if points else code
            # Build [{date:int, value:float|null}]
            out = []
            for p in points:
                v = p["value"]
                out.append({
                    "date": int(p["date"]),
                    "value": float(v) if v is not None else None
                })
            # Sort ascending by date
            out.sort(key=lambda x: x["date"])
            series.append({"code": code, "name": name, "points": out})
        return Response({"country": country, "start": int(start), "end": int(end), "series": series})