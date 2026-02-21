from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sympy as sp
import re
import os
from pathlib import Path

app = FastAPI()

# Bestimmen, ob wir lokal oder auf Vercel laufen
IS_VERCEL = "VERCEL" in os.environ

class EquationRequest(BaseModel):
    equation: str

@app.post("/api/solve")
async def solve_equation(request: EquationRequest):
    eq_str = request.equation.replace(" ", "")
    
    # Basic validation for "="
    if "=" not in eq_str:
        raise HTTPException(status_code=400, detail="Die Gleichung muss ein '=' Zeichen enthalten.")
    
    try:
        # Split into left and right sides
        lhs_str, rhs_str = eq_str.split("=", 1)
        
        # Parse into SymPy expressions with transformations
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
        
        transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
        
        lhs = parse_expr(lhs_str, transformations=transformations)
        rhs = parse_expr(rhs_str, transformations=transformations)
        
        # Formulate equation: lhs - rhs = 0
        equation = sp.Eq(lhs, rhs)
        
        # Identify variables
        variables = equation.free_symbols
        
        if len(variables) == 0:
            raise HTTPException(status_code=400, detail="Keine Variable in der Gleichung gefunden.")
        if len(variables) > 1:
            vars_str = ", ".join(map(str, variables))
            raise HTTPException(status_code=400, detail=f"Mehrere Variablen gefunden: {vars_str}. Nur eine Variable wird unterstützt.")
        
        var = list(variables)[0]
        
        # Check if linear
        if not sp.degree(lhs - rhs, var) == 1:
             raise HTTPException(status_code=400, detail="Nur lineare Gleichungen werden unterstützt.")
        
        # Solve
        solutions = sp.solve(equation, var)
        
        if not solutions:
            return {"result": "Keine Lösung"}
        
        # Return the first (and should be only) solution for linear eq
        result = solutions[0]
        
        # Convert to string or float for JSON
        result_str = str(result)
            
        return {
            "variable": str(var),
            "solution": result_str,
            "numeric_solution": float(result.evalf())
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Ungültiges Gleichungsformat: {str(e)}")

@app.get("/api/health")
async def health():
    return {"status": "ok"}

# Statische Dateien NUR lokal bereitstellen
if not IS_VERCEL:
    BASE_DIR = Path(__file__).resolve().parent.parent
    PUBLIC_DIR = BASE_DIR / "public"
    if PUBLIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(PUBLIC_DIR), html=True), name="public")
