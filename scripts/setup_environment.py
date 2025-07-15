#!/usr/bin/env python3
"""
Environment Setup Script for Google MCP Toolbox with Supabase OAuth

This script helps users set up the necessary environment variables
for integrating Supabase OAuth with Google MCP Toolbox.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with necessary environment variables"""
    
    env_content = """# Google MCP Toolbox 및 Supabase OAuth 환경 변수 설정
# 이 파일의 값들을 실제 값으로 교체하세요.

# Google MCP Toolbox 설정
GOOGLE_MCP_ENDPOINT=https://your-mcp-endpoint.com
GOOGLE_MCP_API_KEY=your-api-key-here

# Google Cloud 인증 설정
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Supabase 설정
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# OAuth 설정
OAUTH_REDIRECT_URL=http://localhost:3000/auth/callback
OAUTH_CLIENT_ID=your-oauth-client-id
OAUTH_CLIENT_SECRET=your-oauth-client-secret

# 로깅 설정
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# 보안 설정
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# 캐싱 설정
CACHE_TTL=3600
CACHE_TYPE=memory

# 환경 설정
ENVIRONMENT=development
DEBUG=true
"""
    
    env_file = Path(".env")
    
    if env_file.exists():
        response = input(".env 파일이 이미 존재합니다. 덮어쓰시겠습니까? (y/N): ")
        if response.lower() != 'y':
            print("❌ 환경 파일 생성이 취소되었습니다.")
            return False
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✅ .env 파일이 생성되었습니다: {env_file.absolute()}")
    return True

def setup_supabase_oauth():
    """Guide user through Supabase OAuth setup"""
    
    print("🔧 Supabase OAuth 설정 가이드")
    print("=" * 50)
    
    print("\n1. Supabase 프로젝트 설정:")
    print("   - https://app.supabase.com 접속")
    print("   - 프로젝트 선택 또는 새로 생성")
    print("   - Settings > API 메뉴로 이동")
    print("   - Project URL과 anon/public key 복사")
    
    print("\n2. OAuth Provider 설정:")
    print("   - Authentication > Providers 메뉴로 이동")
    print("   - Google OAuth 활성화")
    print("   - Client ID와 Client Secret 설정")
    print("   - Redirect URL 설정: http://localhost:3000/auth/callback")
    
    print("\n3. Google OAuth 설정:")
    print("   - https://console.cloud.google.com 접속")
    print("   - APIs & Services > Credentials 메뉴로 이동")
    print("   - OAuth 2.0 Client ID 생성")
    print("   - Authorized redirect URIs 추가:")
    print("     - https://your-project.supabase.co/auth/v1/callback")
    print("     - http://localhost:3000/auth/callback")
    
    print("\n4. 환경 변수 설정:")
    print("   - .env 파일을 수정하여 실제 값들을 입력하세요")
    print("   - 특히 SUPABASE_URL과 SUPABASE_ANON_KEY는 필수입니다")

def install_dependencies():
    """Install additional dependencies for Supabase integration"""
    
    print("\n📦 Supabase 의존성 설치")
    print("=" * 30)
    
    dependencies = [
        "supabase",
        "python-dotenv",
        "fastapi",
        "uvicorn",
        "httpx"
    ]
    
    print("설치할 패키지들:")
    for dep in dependencies:
        print(f"  - {dep}")
    
    response = input("\n설치를 진행하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("❌ 패키지 설치가 취소되었습니다.")
        return False
    
    for dep in dependencies:
        print(f"📦 Installing {dep}...")
        exit_code = os.system(f"pip install {dep}")
        if exit_code != 0:
            print(f"❌ {dep} 설치 실패")
            return False
    
    print("✅ 모든 의존성 설치 완료!")
    return True

def create_callback_server():
    """Create a simple callback server for OAuth"""
    
    callback_server_content = '''"""
OAuth Callback Server for Supabase Integration

This server handles OAuth callbacks from Supabase.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn
import os

app = FastAPI(title="OAuth Callback Server")

@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Handle OAuth callback from Supabase"""
    
    # Get the access token from the URL fragment
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OAuth Callback</title>
    </head>
    <body>
        <h1>OAuth Authentication</h1>
        <p>Please copy the access token below:</p>
        <div id="token-display"></div>
        
        <script>
            // Extract token from URL fragment
            const fragment = window.location.hash.substring(1);
            const params = new URLSearchParams(fragment);
            const accessToken = params.get('access_token');
            
            if (accessToken) {
                document.getElementById('token-display').innerHTML = 
                    `<strong>Access Token:</strong><br><code>${accessToken}</code>`;
            } else {
                document.getElementById('token-display').innerHTML = 
                    '<p>No access token found in URL</p>';
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    print("🚀 Starting OAuth callback server...")
    print("🌐 Server will be available at: http://localhost:3000")
    print("🔗 Callback URL: http://localhost:3000/auth/callback")
    
    uvicorn.run(app, host="0.0.0.0", port=3000)
'''
    
    callback_file = Path("scripts/oauth_callback_server.py")
    
    with open(callback_file, 'w', encoding='utf-8') as f:
        f.write(callback_server_content)
    
    print(f"✅ OAuth callback server created: {callback_file.absolute()}")
    print("   실행하려면: python scripts/oauth_callback_server.py")

def main():
    """Main function"""
    
    print("🔧 Google MCP Toolbox - Supabase OAuth 환경 설정")
    print("=" * 60)
    
    print("\n선택하세요:")
    print("1. 환경 변수 파일 생성 (.env)")
    print("2. Supabase OAuth 설정 가이드 보기")
    print("3. 의존성 패키지 설치")
    print("4. OAuth 콜백 서버 생성")
    print("5. 전체 설정 (1-4 모두 실행)")
    print("0. 종료")
    
    while True:
        choice = input("\n선택: ")
        
        if choice == "0":
            print("👋 설정을 종료합니다.")
            break
        elif choice == "1":
            create_env_file()
        elif choice == "2":
            setup_supabase_oauth()
        elif choice == "3":
            install_dependencies()
        elif choice == "4":
            create_callback_server()
        elif choice == "5":
            print("🔧 전체 설정을 시작합니다...")
            create_env_file()
            setup_supabase_oauth()
            install_dependencies()
            create_callback_server()
            print("✅ 전체 설정이 완료되었습니다!")
        else:
            print("❌ 잘못된 선택입니다. 다시 선택해주세요.")

if __name__ == "__main__":
    main() 