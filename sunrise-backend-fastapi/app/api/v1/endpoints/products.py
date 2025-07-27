from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_products():
    """Get all products"""
    return {"message": "Get products endpoint - to be implemented", "products": []}


@router.post("/")
async def create_product():
    """Create a new product"""
    return {"message": "Create product endpoint - to be implemented"}


@router.get("/{product_id}")
async def get_product(product_id: int):
    """Get product by ID"""
    return {"message": f"Get product {product_id} endpoint - to be implemented"}


@router.put("/{product_id}")
async def update_product(product_id: int):
    """Update product by ID"""
    return {"message": f"Update product {product_id} endpoint - to be implemented"}


@router.delete("/{product_id}")
async def delete_product(product_id: int):
    """Delete product by ID"""
    return {"message": f"Delete product {product_id} endpoint - to be implemented"}
