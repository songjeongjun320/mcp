"""
실제 프로덕션 환경에서 사용하는 예제

이 예제는 실제 Google MCP Toolbox 서비스와 연결하여 사용하는 방법을 보여줍니다.
"""

import asyncio
import os
import sys
from pathlib import Path

# 프로젝트 root 디렉토리를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from toolbox_integration import ToolboxClientWrapper
from toolbox_integration.auth import GoogleAuthProvider, StaticTokenProvider

async def production_example():
    """실제 프로덕션 환경에서 사용하는 예제"""
    
    print("🚀 Google MCP Toolbox - 프로덕션 예제")
    print("=" * 50)
    
    # 환경 변수 확인
    endpoint = os.getenv("GOOGLE_MCP_ENDPOINT")
    api_key = os.getenv("GOOGLE_MCP_API_KEY")
    
    if not endpoint:
        print("❌ GOOGLE_MCP_ENDPOINT 환경 변수가 설정되지 않았습니다.")
        print("💡 .env 파일에 다음을 추가하세요:")
        print("   GOOGLE_MCP_ENDPOINT=https://your-actual-endpoint.com")
        return
    
    print(f"🔗 연결 대상: {endpoint}")
    
    # 인증 방법 선택
    auth_provider = None
    
    if api_key:
        # API 키 인증
        auth_provider = StaticTokenProvider(api_key)
        print("🔑 API 키 인증 사용")
    
    elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        # Google Cloud 인증
        auth_provider = GoogleAuthProvider()
        print("🔑 Google Cloud 인증 사용")
    
    else:
        print("⚠️  인증 정보가 없습니다. Mock 모드로 실행합니다.")
        print("💡 실제 사용을 위해 .env 파일에 인증 정보를 추가하세요:")
        print("   GOOGLE_MCP_API_KEY=your-api-key")
        print("   또는")
        print("   GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json")
    
    # 클라이언트 생성
    client = ToolboxClientWrapper(
        service_endpoint=endpoint,
        auth_provider=auth_provider
    )
    
    try:
        # 연결 시도
        print("\n🔌 서비스 연결 중...")
        await client.connect()
        
        # 헬스 체크
        is_healthy = await client.health_check()
        if is_healthy:
            print("✅ 서비스 정상 작동")
            
            # 실제 작업 수행
            await perform_real_work(client)
            
        else:
            print("❌ 서비스 연결 실패")
            print("💡 서비스 엔드포인트와 인증 정보를 확인하세요.")
            
    except Exception as e:
        print(f"❌ 연결 에러: {e}")
        print("💡 가능한 해결 방법:")
        print("   1. 서비스 엔드포인트 확인")
        print("   2. 인증 정보 확인")
        print("   3. 네트워크 연결 확인")
        
    finally:
        await client.disconnect()
        print("🔌 연결 종료")

async def perform_real_work(client):
    """실제 업무 수행"""
    
    print("\n📋 사용 가능한 도구 목록:")
    tools = await client.list_tools()
    
    for i, tool in enumerate(tools[:5], 1):  # 처음 5개만 표시
        print(f"   {i}. {tool.name}: {tool.description}")
    
    if tools:
        print(f"\n🔧 첫 번째 도구 사용: {tools[0].name}")
        
        # 실제 도구 사용
        result = await client.call_tool(
            tools[0].name,
            parameters={"input": "Hello, World!"}
        )
        
        print(f"📤 결과: {result}")
    
    print("\n✅ 작업 완료!")

def setup_environment_guide():
    """환경 설정 가이드"""
    
    print("🔧 환경 설정 가이드")
    print("=" * 30)
    
    print("\n1. .env 파일 생성:")
    print("   python scripts/setup_environment.py")
    
    print("\n2. 필수 환경 변수:")
    print("   GOOGLE_MCP_ENDPOINT=https://your-service-endpoint.com")
    
    print("\n3. 인증 방법 (둘 중 하나):")
    print("   방법 A - API 키:")
    print("   GOOGLE_MCP_API_KEY=your-api-key")
    print("")
    print("   방법 B - Google Cloud 인증:")
    print("   GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json")
    
    print("\n4. 실행:")
    print("   python examples/production_example.py")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_environment_guide()
    else:
        asyncio.run(production_example()) 