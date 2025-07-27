from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_submenus():
    """Get all submenus"""
    return {"message": "Get submenus endpoint - to be implemented", "submenus": []}


@router.post("/")
async def create_submenu():
    """Create a new submenu"""
    return {"message": "Create submenu endpoint - to be implemented"}


@router.get("/{submenu_id}")
async def get_submenu(submenu_id: int):
    """Get submenu by ID"""
    return {"message": f"Get submenu {submenu_id} endpoint - to be implemented"}


@router.put("/{submenu_id}")
async def update_submenu(submenu_id: int):
    """Update submenu by ID"""
    return {"message": f"Update submenu {submenu_id} endpoint - to be implemented"}


@router.delete("/{submenu_id}")
async def delete_submenu(submenu_id: int):
    """Delete submenu by ID"""
    return {"message": f"Delete submenu {submenu_id} endpoint - to be implemented"}
