"""
Supabase OAuth Integration Example with Google MCP Toolbox

This example shows how to integrate Supabase OAuth authentication
with the Google MCP Toolbox client.
"""

import os
import asyncio
from typing import Optional

from supabase import create_client, Client
from toolbox_integration import ToolboxClientWrapper
from toolbox_integration.auth import CustomTokenProvider
from config.settings import Settings

# Supabase OAuth Provider Class
class SupabaseOAuthProvider:
    """Supabase OAuth authentication provider"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.session = None
    
    async def authenticate_with_oauth(self, provider: str = "google") -> Optional[str]:
        """
        Authenticate with OAuth provider through Supabase
        
        Args:
            provider: OAuth provider (google, github, etc.)
            
        Returns:
            Access token if successful, None otherwise
        """
        try:
            # OAuth 로그인 URL 생성
            auth_url = self.supabase.auth.sign_in_with_oauth({
                "provider": provider,
                "options": {
                    "redirect_to": "http://localhost:3000/auth/callback"
                }
            })
            
            print(f"Please visit this URL to authenticate: {auth_url}")
            
            # 실제 구현에서는 웹 서버를 띄우고 callback을 받아야 함
            # 여기서는 예제를 위해 수동으로 토큰 입력
            access_token = input("Enter the access token from callback: ")
            
            # 토큰으로 세션 설정
            response = self.supabase.auth.set_session(access_token, "")
            
            if response.session:
                self.session = response.session
                return response.session.access_token
                
        except Exception as e:
            print(f"OAuth authentication failed: {e}")
            return None
    
    async def get_user_info(self):
        """Get current user information"""
        if self.session:
            return self.supabase.auth.get_user()
        return None
    
    async def sign_out(self):
        """Sign out current user"""
        self.supabase.auth.sign_out()
        self.session = None

# Custom Token Provider for Supabase
class SupabaseTokenProvider(CustomTokenProvider):
    """Custom token provider using Supabase OAuth"""
    
    def __init__(self, supabase_oauth: SupabaseOAuthProvider):
        self.supabase_oauth = supabase_oauth
        super().__init__(self._get_token)
    
    async def _get_token(self) -> Optional[str]:
        """Get token from Supabase OAuth session"""
        if self.supabase_oauth.session:
            return self.supabase_oauth.session.access_token
        return None

# Integration Example
class SupabaseGoogleMCPIntegration:
    """Integration between Supabase OAuth and Google MCP Toolbox"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_oauth = SupabaseOAuthProvider(supabase_url, supabase_key)
        self.token_provider = SupabaseTokenProvider(self.supabase_oauth)
        self.toolbox_client = None
    
    async def initialize(self):
        """Initialize the integration"""
        # 1. Supabase OAuth 인증
        print("🔐 Starting Supabase OAuth authentication...")
        token = await self.supabase_oauth.authenticate_with_oauth("google")
        
        if not token:
            raise Exception("Failed to authenticate with Supabase OAuth")
        
        print("✅ Supabase OAuth authentication successful!")
        
        # 2. 사용자 정보 가져오기
        user_info = await self.supabase_oauth.get_user_info()
        if user_info:
            print(f"👤 Logged in as: {user_info.user.email}")
        
        # 3. Google MCP Toolbox 클라이언트 초기화
        print("🚀 Initializing Google MCP Toolbox client...")
        self.toolbox_client = ToolboxClientWrapper(
            auth_provider=self.token_provider,
            service_endpoint="https://your-service-endpoint.com"
        )
        
        # 4. 클라이언트 연결 테스트
        await self.toolbox_client.connect()
        print("✅ Google MCP Toolbox client connected successfully!")
        
        return True
    
    async def use_toolbox_features(self):
        """Use Google MCP Toolbox features"""
        if not self.toolbox_client:
            raise Exception("Client not initialized")
        
        try:
            # 예제: 도구 목록 가져오기
            tools = await self.toolbox_client.list_tools()
            print(f"📋 Available tools: {len(tools)}")
            
            # 예제: 특정 도구 사용
            if tools:
                tool_name = tools[0].name
                result = await self.toolbox_client.call_tool(
                    tool_name,
                    parameters={"query": "test"}
                )
                print(f"🔧 Tool result: {result}")
            
        except Exception as e:
            print(f"❌ Error using toolbox features: {e}")
    
    async def cleanup(self):
        """Clean up resources"""
        if self.toolbox_client:
            await self.toolbox_client.disconnect()
        await self.supabase_oauth.sign_out()
        print("🧹 Cleanup completed")

# Main execution
async def main():
    """Main function demonstrating the integration"""
    
    # 환경 변수에서 Supabase 설정 가져오기
    supabase_url = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
    supabase_key = os.getenv("SUPABASE_ANON_KEY", "your-anon-key")
    
    if not supabase_url or not supabase_key:
        print("❌ Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
        return
    
    integration = SupabaseGoogleMCPIntegration(supabase_url, supabase_key)
    
    try:
        # 초기화
        await integration.initialize()
        
        # 기능 사용
        await integration.use_toolbox_features()
        
    except Exception as e:
        print(f"❌ Integration failed: {e}")
    
    finally:
        # 정리
        await integration.cleanup()

# Environment setup helper
def setup_environment():
    """Setup environment variables for Supabase"""
    
    print("🔧 Setting up Supabase environment variables...")
    print("\n1. Go to your Supabase dashboard (https://app.supabase.com)")
    print("2. Select your project")
    print("3. Go to Settings > API")
    print("4. Copy the Project URL and anon/public key")
    print("5. Set the following environment variables:")
    print("\n   Windows:")
    print("   set SUPABASE_URL=https://your-project.supabase.co")
    print("   set SUPABASE_ANON_KEY=your-anon-key")
    print("\n   Linux/Mac:")
    print("   export SUPABASE_URL=https://your-project.supabase.co")
    print("   export SUPABASE_ANON_KEY=your-anon-key")
    print("\n6. Enable OAuth providers in Authentication > Providers")
    print("7. Configure redirect URLs in your OAuth provider settings")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_environment()
    else:
        asyncio.run(main()) 