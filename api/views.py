from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.db import IntegrityError
from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
import requests
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

#Auth
@method_decorator(ensure_csrf_cookie, name="dispatch")
class CSRF(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Sets CSRF cookies and returns the token"""
        # Ensure CSRF token is set
        csrf_token = get_token(request)
        logger.info(f"CSRF token generated: {csrf_token}")
        return Response({"detail": "CSRF cookies set", "csrfToken": csrf_token})

class Register(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        logger.info(f"Register attempt: {request.data}")
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email", "")
        
        if not username or not password:
            logger.warning("Registration failed: missing username or password")
            return Response({"detail": "username and password required"}, status=400)
            
        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            logger.info(f"User registered successfully: {username}")
            return Response({"detail": "User Registered Successfully"})
        except IntegrityError:
            logger.warning(f"Registration failed: username {username} already exists")
            return Response({"detail": "Username already exists please choose another username"}, status=400)

class Login(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        logger.info(f"Login attempt for: {request.data.get('username')}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request cookies: {request.COOKIES}")
        
        username = request.data.get("username")
        password = request.data.get("password")
        
        if not username or not password:
            logger.warning("Login failed: missing credentials")
            return Response({"detail": "Username and password are required"}, status=400)
        
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            logger.warning(f"Login failed: invalid credentials for {username}")
            return Response({"detail": "Invalid credentials"}, status=400)
            
        login(request, user)
        logger.info(f"User logged in successfully: {username}")
        
        return Response({
            "username": user.username, 
            "email": user.email,
            "detail": "Login successful"
        })

class Logout(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        logger.info(f"Logout for user: {getattr(request.user, 'username', 'anonymous')}")
        logout(request)
        return Response({"detail": "User logged out successfully"})

class UserView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            logger.warning("User view accessed by unauthenticated user")
            return Response({"authenticated": False}, status=401)
            
        u = request.user
        logger.info(f"User view accessed by: {u.username}")
        return Response({
            "authenticated": True, 
            "username": u.username, 
            "email": u.email
        })
    
class Indicators(APIView):
    """
    Query params:
      country: e.g. IN
      codes: comma-separated indicator codes (e.g. NY.GDP.MKTP.CD,SP.POP.TOTL)
      start: year (e.g. 2000)
      end: year (e.g. 2023)
    """
    def get(self, request):
        logger.info(f"Indicators request by user: {getattr(request.user, 'username', 'anonymous')}")
        
        country = request.query_params.get("country", "IN")
        codes = request.query_params.get("codes", "NY.GDP.MKTP.CD,SP.POP.TOTL").split(",")
        start = request.query_params.get("start", "2000")
        end = request.query_params.get("end", "2023")

        logger.info(f"Fetching indicators: country={country}, codes={codes}, start={start}, end={end}")

        base = "https://api.worldbank.org/v2/country/{country}/indicator/{code}?format=json&per_page=20000&date={start}:{end}"
        series = []
        
        for code in codes:
            url = base.format(country=country, code=code.strip(), start=start, end=end)
            logger.info(f"Fetching from World Bank API: {url}")
            
            try:
                r = requests.get(url, timeout=20)
                if r.status_code != 200:
                    logger.error(f"World Bank API error for {code}: {r.status_code}")
                    return Response({"detail": "world bank error", "code": code}, status=502)
                    
                data = r.json()
                if not isinstance(data, list) or len(data) < 2:
                    logger.warning(f"No data returned for indicator {code}")
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
                logger.info(f"Successfully processed indicator {code}: {len(out)} data points")
                
            except requests.RequestException as e:
                logger.error(f"Request error for {code}: {str(e)}")
                return Response({"detail": "Failed to fetch data from World Bank", "error": str(e)}, status=502)
            except Exception as e:
                logger.error(f"Unexpected error processing {code}: {str(e)}")
                return Response({"detail": "Data processing error", "error": str(e)}, status=500)
                
        logger.info(f"Returning {len(series)} series")
        return Response({
            "country": country, 
            "start": int(start), 
            "end": int(end), 
            "series": series
        })
