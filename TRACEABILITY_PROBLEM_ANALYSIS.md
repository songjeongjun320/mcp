# Traceability MCP 문제점 분석 및 해결

## 🔴 발견된 주요 문제

### 1. 핵심 기능 누락
**문제:** 프로젝트 전체의 트리 뷰를 보여주는 도구가 없었습니다.

**기존 도구들:**
- ❌ `traceability_query_hierarchy` - 특정 **requirement_id**가 필요함
- ❌ `traceability_validate_cycle` - 관계 생성 전 검증용
- ❌ `traceability_search_for_linking` - 검색 용도
- ❌ `traceability_generate_matrix` - 매트릭스 형식 (트리 아님)

**문제점:**
```
사용자 워크플로우:
1. pull_projects() → project_id 획득
2. ??? → 막힘! 트리를 보려면 개별 requirement_id가 필요함
3. 하지만 requirement_id를 어떻게 아는가?
```

### 2. `get_requirement_tree()` 함수 미사용

**how_to_show_tree_view.md에 명시된 핵심 함수:**
```sql
-- 위치: DB_Analyze/update_tree_function.sql
-- 이 함수가 프로젝트의 전체 계층 구조를 반환
get_requirement_tree(p_project_id UUID)
```

**반환 데이터 구조:**
- `requirement_id`: UUID
- `title`: external_id 또는 name
- `parent_id`: 부모 노드 UUID (root는 NULL)
- `depth`: 0 (root), 1, 2, ... (계층 레벨)
- `path`: "REQ-001 > REQ-002 > REQ-003"
- `has_children`: 자식 노드 존재 여부

**이 함수를 MCP에서 전혀 사용하지 않았음!**

## ✅ 해결 방법

### 새로운 도구 추가: `traceability_get_tree`

**파일:** `tools/traceability_get_tree_tool.py`

**기능:**
1. `project_id`만 받아서 전체 트리 구조 반환
2. `get_requirement_tree()` PostgreSQL 함수 호출
3. UI 필터링 로직 적용:
   - `has_children = true` 또는 `depth > 0`인 노드만 표시
   - 고아 노드(orphan nodes) 제외
4. `path`로 정렬하여 계층 구조 유지

**올바른 워크플로우:**
```
1. pull_projects(organization_id, "show projects")
   → 프로젝트 목록 및 project_id 획득

2. traceability_get_tree(organization_id, project_id)
   → 전체 트리 뷰 표시
   → Root 노드부터 모든 계층 구조 확인
```

## 📊 데이터베이스 구조 이해

### `requirements_closure` 테이블 (Closure Table)
```sql
ancestor_id   | descendant_id | depth | path
-------------|---------------|-------|---------------------
REQ-001      | REQ-002       | 1     | REQ-001 > REQ-002
REQ-001      | REQ-003       | 2     | REQ-001 > REQ-002 > REQ-003
```

- `depth = 1`: 직접적인 부모-자식 관계
- `depth > 1`: 조상-후손 관계
- 모든 조상-후손 관계를 자동으로 저장

### `get_requirement_tree()` 함수 동작 방식

1. **Root 노드 선택 (depth = 0)**
   ```sql
   -- requirements_closure에서 descendant로 나타나지 않는 requirement = Root
   WHERE NOT EXISTS (
       SELECT 1 FROM requirements_closure rc
       WHERE rc.descendant_id = r.id AND rc.depth = 1
   )
   ```

2. **재귀적으로 자식 노드 탐색**
   ```sql
   -- depth = 1로 필터링하여 직접적인 부모-자식 관계만 조회
   JOIN requirements_closure rc ON rc.ancestor_id = t.requirement_id AND rc.depth = 1
   ```

## 🎯 도구별 사용 목적

### 1. `traceability_get_tree` ⭐ **PRIMARY**
- **목적:** 프로젝트 전체 트리 뷰 보기
- **입력:** project_id
- **출력:** 전체 계층 구조
- **사용 시기:** "프로젝트의 요구사항 계층을 보여줘"

### 2. `traceability_query_hierarchy`
- **목적:** 특정 요구사항의 부모/자식 관계 조회
- **입력:** requirement_id + direction (ancestors/descendants/both)
- **출력:** 해당 요구사항의 관계들
- **사용 시기:** "이 요구사항의 부모는?"

### 3. `traceability_validate_cycle`
- **목적:** 순환 참조 방지
- **입력:** ancestor_id + descendant_id
- **출력:** 순환이 생기는지 여부
- **사용 시기:** 관계 생성 전 검증

### 4. `traceability_search_for_linking`
- **목적:** 연결 가능한 요구사항 검색
- **입력:** 검색 쿼리, 필터
- **출력:** 검색 결과
- **사용 시기:** "연결할 요구사항을 찾아줘"

### 5. `traceability_generate_matrix`
- **목적:** 매트릭스 형태로 요구사항 관계 보기
- **입력:** project_id
- **출력:** 요구사항별 링크 수, 통계
- **사용 시기:** "커버리지 통계를 보여줘"

## 📝 예제 사용 시나리오

### 시나리오 1: 프로젝트 트레이서빌리티 확인
```
User: "Automated Driving 프로젝트의 요구사항 계층을 보여줘"

Step 1: pull_projects(org_id, "show Automated Driving project")
→ project_id: "c41a1968-dafe-466b-98c2-bcf8a5e71584"

Step 2: traceability_get_tree(org_id, project_id)
→ 결과:
  [
    {
      requirement_id: "...",
      title: "REQ-001",
      parent_id: null,
      depth: 0,
      path: "REQ-001",
      has_children: true
    },
    {
      requirement_id: "...",
      title: "REQ-002",
      parent_id: "...",
      depth: 1,
      path: "REQ-001 > REQ-002",
      has_children: false
    }
  ]
```

### 시나리오 2: 특정 요구사항의 자식 확인
```
User: "REQ-001의 모든 자식 요구사항을 보여줘"

traceability_query_hierarchy(org_id, req_id, "descendants")
```

## 🔧 코드 변경사항

### 추가된 파일
1. `tools/traceability_get_tree_tool.py` - 새로운 메인 도구

### 수정된 파일
1. `mcp_server.py`
   - Import 추가
   - `traceability_get_tree()` wrapper 함수 추가
   - 도구 등록 (리스트 최상단에 배치)

## ✅ 해결 완료

이제 올바른 워크플로우가 가능합니다:
```
pull_projects → project_id → traceability_get_tree → 전체 계층 구조 확인
```

**Tree View가 이제 제대로 동작합니다!**
