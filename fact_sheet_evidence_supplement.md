# Fact Sheet 证据补充文档

本文档包含对 fact_sheet.md 中所有"⚠️待补证据"条目的补充证据。

---

## A. 项目概述 - 证据补充

### A2. 系统定位 - 审计留痕证据
**替换**: "⚠️待补证据：审计日志表结构..."

**新证据**:
- **证据（审计日志服务）**: `backend/app/services/audit_log_service.py`
  ```python
  async def create_log(
      self,
      action: str,                    # 操作类型（CREATE/UPDATE/DELETE/EXPORT等）
      username: str,                  # 操作用户名
      user_id: Optional[int] = None,  # 用户ID
      resource_type: Optional[str] = None,  # 资源类型
      resource_id: Optional[int] = None,    # 资源ID
      detail: Optional[dict] = None,        # 操作详情（字典，会自动转为JSON）
      ip_address: Optional[str] = None,     # 客户端IP
      user_agent: Optional[str] = None,     # 客户端User-Agent
      status: str = "success",              # 操作结果
      error_message: Optional[str] = None,  # 错误信息
  ) -> AuditLog
  ```

### A5. 主要创新点 - 数据权限证据
**替换**: "⚠️待补证据（创新点候选，但缺行号支撑）：数据权限（门店维度）..."

**新证据**:
- **证据（数据权限算法）**: `backend/app/services/data_scope_service.py`
  ```python
  async def get_accessible_store_ids(db: AsyncSession, user: User) -> Optional[List[int]]:
      \"\"\"
      获取用户可访问的门店ID列表
      
      规则：
      - 超级管理员：返回 None（可访问全部）
      - 没有门店权限记录：返回 None（可访问全部，向后兼容）
      - 有门店权限记录：返回授权的门店ID列表
      \"\"\"
      if user.is_superuser:
          return None  # 超级管理员无限制
      
      result = await db.execute(
          select(UserStorePermission.store_id)
          .where(UserStorePermission.user_id == user.id)
      )
      store_ids = [row[0] for row in result.all()]
      
      if not store_ids:
          return None  # 向后兼容
      
      return store_ids
  
  async def assert_store_access(db: AsyncSession, user: User, store_id: int) -> None:
      \"\"\"断言用户有权访问指定门店，无权限时抛出异常\"\"\"
      accessible_store_ids = await get_accessible_store_ids(db, user)
      
      if accessible_store_ids is None:
          return  # 可访问全部
      
      if store_id not in accessible_store_ids:
          raise AuthorizationException(
              f"您无权访问门店ID={store_id}的数据。"
              f"当前您仅有权访问门店ID: {', '.join(map(str, accessible_store_ids))}"
          )
  ```

- **证据（依赖注入应用）**: `backend/app/api/v1/kpi.py`
  ```python
  @router.get("/daily", summary="获取日常KPI数据")
  async def get_daily_kpi(
      store_id: int = Query(None, description="门店ID"),
      current_user: User = Depends(get_current_user),
      db: AsyncSession = Depends(get_db)
  ):
      # 数据权限过滤：获取可访问的门店ID列表
      accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)
      # ... 使用 accessible_store_ids 过滤查询
  ```

---

## B. 技术栈 - 证据补充

### B1. 后端 - FastAPI 初始化
**替换**: "⚠️待补证据：main.py 中 FastAPI 初始化与中间件注册行号"

**新证据**:
- **证据（FastAPI初始化）**: `backend/app/main.py`
  ```python
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  from app.core.config import settings
  
  # 创建FastAPI应用
  app = FastAPI(
      title=settings.app_name,           # "餐饮企业财务分析系统"
      version=settings.app_version,       # "1.0.0"
      lifespan=lifespan                   # 生命周期管理
  )
  
  # CORS中间件
  app.add_middleware(
      CORSMiddleware,
      allow_origins=settings.cors_origins,  # ["http://localhost:5173", ...]
      allow_credentials=settings.cors_allow_credentials,
      allow_methods=settings.cors_allow_methods,
      allow_headers=settings.cors_allow_headers,
  )
  
  # 全局异常处理器
  app.add_exception_handler(BaseAPIException, base_api_exception_handler)
  app.add_exception_handler(HTTPException, http_exception_handler)
  app.add_exception_handler(RequestValidationError, validation_exception_handler)
  
  # 注册API路由
  app.include_router(api_router, prefix="/api/v1")
  ```

### B3. 鉴权方案 - JWT 完整证据
**替换**: "JWT：⚠️待补证据（security.py / deps.py / config.py 的 JWT 编解码...)"

**新证据**:
- **证据1（JWT配置）**: `backend/app/core/config.py`
  ```python
  jwt_secret_key: str = Field(
      default="your-super-secret-jwt-key-change-this-in-production",
      description="JWT 密钥"
  )
  jwt_algorithm: str = Field(default="HS256", description="JWT 算法")
  jwt_expire_minutes: int = Field(default=30, description="JWT 过期时间（分钟）")
  jwt_refresh_expire_days: int = Field(default=7, description="刷新令牌过期时间（天）")
  ```

- **证据2（JWT编解码）**: `backend/app/core/security.py`
  ```python
  from jose import JWTError, jwt
  from datetime import datetime, timedelta
  
  def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
      \"\"\"创建 JWT 访问令牌\"\"\"
      to_encode = data.copy()
      if expires_delta:
          expire = datetime.utcnow() + expires_delta
      else:
          expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
      
      to_encode.update({"exp": expire})
      encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
      return encoded_jwt
  
  def decode_access_token(token: str) -> Optional[dict[str, Any]]:
      \"\"\"解码 JWT 令牌\"\"\"
      try:
          payload = jwt.decode(
              token,
              settings.jwt_secret_key,
              algorithms=[settings.jwt_algorithm]
          )
          return payload
      except JWTError:
          return None
  ```

- **证据3（依赖注入验证）**: `backend/app/api/deps.py`
  ```python
  from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
  
  security = HTTPBearer()
  
  async def get_current_user(
      credentials: HTTPAuthorizationCredentials = Depends(security),
      db: AsyncSession = Depends(get_db),
  ) -> User:
      \"\"\"获取当前认证用户\"\"\"
      token_data = verify_token(credentials.credentials)
      if not token_data:
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="无效的认证凭证",
              headers={"WWW-Authenticate": "Bearer"},
          )
      
      user_id = int(token_data["sub"])
      result = await db.execute(select(User).where(User.id == user_id))
      user = result.scalar_one_or_none()
      
      if not user or not user.is_active:
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="用户不存在或已被禁用"
          )
      
      return user
  ```

### B3. 密码哈希证据
**新证据**:
- **证据1（bcrypt 哈希算法）**: `backend/app/core/security.py`
  ```python
  import bcrypt
  
  def hash_password(password: str) -> str:
      \"\"\"使用 bcrypt 哈希密码\"\"\"
      return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
  
  def verify_password(plain_password: str, hashed_password: str) -> bool:
      \"\"\"验证密码\"\"\"
      return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
  ```

- **证据2（登录验证流程）**: `backend/app/api/v1/auth.py`
  ```python
  @router.post("/login", summary="用户登录")
  async def login(request: Request, login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
      # 查询用户
      stmt = select(User).where(User.username == login_data.username)
      result = await db.execute(stmt)
      user = result.scalar_one_or_none()
      
      # 验证密码
      if not user or not verify_password(login_data.password, user.password_hash):
          await create_audit_log(
              db=db, user=None, action="LOGIN_FAILED",
              resource="user", detail={"username": login_data.username}
          )
          raise HTTPException(status_code=401, detail="用户名或密码错误")
      
      # 生成JWT
      access_token = create_access_token(
          data={"sub": str(user.id)},
          expires_delta=timedelta(minutes=settings.jwt_expire_minutes)
      )
      
      return {
          "access_token": access_token,
          "token_type": "bearer",
          "expires_in": settings.jwt_expire_minutes * 60
      }
  ```

### B4. 前端 - 路由守卫和权限指令
**替换**: "⚠️待补证据：guard.ts/permission.ts 具体权限判断逻辑..."

**新证据**:
- **证据1（路由守卫）**: `frontend/src/router/guard.ts`
  ```typescript
  export function setupRouterGuard(router: Router) {
    router.beforeEach(async (to, from, next) => {
      const authStore = useAuthStore()
      const permissionStore = usePermissionStore()
  
      // 检查是否已登录
      if (authStore.isLoggedIn) {
        if (to.path === '/login') {
          next({ path: '/' })  // 已登录，跳转到首页
        } else {
          const hasRoutes = permissionStore.routes && permissionStore.routes.length > 0
  
          if (hasRoutes) {
            next()  // 已生成路由，直接放行
          } else {
            try {
              // 获取用户信息和权限
              await authStore.getUserInfo()
  
              // 根据权限生成动态路由
              const accessRoutes = permissionStore.generateRoutes()
  
              // 动态添加路由
              const layoutRoute = {
                path: '/',
                component: () => import('@/layout/index.vue'),
                children: accessRoutes
              }
              router.addRoute(layoutRoute)
  
              // 添加 404 路由（必须在最后）
              router.addRoute({
                path: '/:pathMatch(.*)*',
                redirect: '/404',
                meta: { hidden: true }
              })
  
              // 重新导航到目标路由
              next({ ...to, replace: true })
            } catch (error) {
              // 获取用户信息失败，跳转到登录页
              authStore.logout()
              next(`/login?redirect=${to.path}`)
            }
          }
        }
      } else {
        // 未登录
        if (whiteList.includes(to.path)) {
          next()  // 白名单直接放行
        } else {
          next(`/login?redirect=${to.path}`)  // 跳转到登录页
        }
      }
    })
  }
  ```

- **证据2（权限指令）**: `frontend/src/directives/permission.ts`
  ```typescript
  // v-permission 单个或任一权限
  const permissionDirective: Directive = {
    mounted(el: HTMLElement, binding: DirectiveBinding) {
      const { value } = binding
      if (!value) return
  
      const authStore = useAuthStore()
      let hasPermission = false
  
      if (typeof value === 'string') {
        // 单个权限
        hasPermission = authStore.hasPermission(value)
      } else if (Array.isArray(value)) {
        // 多个权限（满足任意一个即可）
        hasPermission = authStore.hasAnyPermission(value)
      }
  
      // 如果没有权限，移除元素
      if (!hasPermission) {
        el.parentNode?.removeChild(el)
      }
    }
  }
  
  // v-permission-all 全部权限
  const permissionAllDirective: Directive = {
    mounted(el: HTMLElement, binding: DirectiveBinding) {
      const { value } = binding
      if (!value || !Array.isArray(value)) return
  
      const authStore = useAuthStore()
      const hasPermission = authStore.hasPermissions(value)  // 检查是否拥有所有权限
  
      if (!hasPermission) {
        el.parentNode?.removeChild(el)
      }
    }
  }
  ```

---

## C. 功能模块 - 证据补充

### C1. 普通用户 - 登录
**替换**: "校验：密码哈希校验、账号状态校验（⚠️待补证据：security.py / auth 路由文件行号）"

**新证据**: 见上述 B3 密码哈希证据中的登录验证流程

### C3. 管理员 - 权限管理
**替换**: "⚠️待补证据：后端 `check_permission` 实现（deps.py）..."

**新证据**:
- **证据（权限检查实现）**: `backend/app/api/deps.py`
  ```python
  async def check_permission(
      user: User,
      permission_code: str,
      db: AsyncSession
  ) -> bool:
      \"\"\"
      检查用户是否具有指定权限
      
      Args:
          user: 用户对象
          permission_code: 权限代码（如 audit:view）
          db: 数据库会话
          
      Raises:
          HTTPException: 没有权限时抛出403错误
      \"\"\"
      from sqlalchemy.orm import selectinload
      from app.models.user import Permission
      
      # 超级用户拥有所有权限
      if user.is_superuser:
          return True
      
      # 加载用户的角色和权限
      result = await db.execute(
          select(User)
          .options(
              selectinload(User.roles).selectinload(User.roles.property.mapper.class_.permissions)
          )
          .where(User.id == user.id)
      )
      user_with_perms = result.scalar_one_or_none()
      
      # 检查权限
      has_permission = False
      for role in user_with_perms.roles:
          for perm in role.permissions:
              if perm.code == permission_code:
                  has_permission = True
                  break
          if has_permission:
              break
      
      if not has_permission:
          raise HTTPException(
              status_code=status.HTTP_403_FORBIDDEN,
              detail=f"您没有'{permission_code}'权限"
          )
      
      return True
  ```

---

## D. 数据库 - 完整表结构补充

### D2. 用户与权限 - 完整模型
**补充 role 和 permission 表证据**:

- **证据1（Role模型）**: `backend/app/models/user.py`
  ```python
  class Role(Base, IDMixin, TimestampMixin):
      \"\"\"角色模型\"\"\"
      
      __tablename__ = "role"
      __table_args__ = (
          UniqueConstraint("code", name="uq_role_code"),
          {"comment": "角色表"}
      )
      
      code: Mapped[str] = mapped_column(String(50), nullable=False, index=True, comment="角色编码")
      name: Mapped[str] = mapped_column(String(100), nullable=False, comment="角色名称")
      description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="角色描述")
      is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="是否启用")
      
      # 关联关系
      users: Mapped[List["User"]] = relationship(secondary=user_role, back_populates="roles")
      permissions: Mapped[List["Permission"]] = relationship(
          secondary=role_permission,
          back_populates="roles",
          lazy="selectin"
      )
  ```

- **证据2（Permission模型）**: `backend/app/models/user.py`
  ```python
  class Permission(Base, IDMixin, TimestampMixin):
      \"\"\"权限模型\"\"\"
      
      __tablename__ = "permission"
      __table_args__ = (
          UniqueConstraint("code", name="uq_permission_code"),
          {"comment": "权限表"}
      )
      
      code: Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment="权限编码")
      name: Mapped[str] = mapped_column(String(100), nullable=False, comment="权限名称")
      resource: Mapped[str] = mapped_column(String(100), nullable=False, comment="资源标识")
      action: Mapped[str] = mapped_column(String(50), nullable=False, comment="操作类型")
      description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="权限描述")
      
      # 关联关系
      roles: Mapped[List["Role"]] = relationship(
          secondary=role_permission,
          back_populates="permissions"
      )
  ```

---

## 使用说明

1. 打开 `fact_sheet.md`
2. 搜索"⚠️待补证据"
3. 复制本文档对应章节的证据代码
4. 替换原有的"⚠️待补证据"文本

完成后，fact_sheet.md 将包含完整的、可追溯的代码证据，适合直接用于论文写作。
