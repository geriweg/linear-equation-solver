from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sympy as sp
import re
import os
from pathlib import Path

app = FastAPI()

# Prüfen, ob wir in der Vercel-Umgebung sind
IS_VERCEL = "VERCEL" in os.environ

class EquationRequest(BaseModel):
    equation: str

@app.post("/api/solve")
async def solve_equation(request: EquationRequest):
    eq_str = request.equation.replace(" ", "")
    
    # Basis-Validierung auf "="
    if "=" not in eq_str:
        raise HTTPException(status_code=400, detail="Die Gleichung muss ein '=' Zeichen enthalten.")
    
    try:
        # Aufteilung in linke und rechte Seite
        lhs_str, rhs_str = eq_str.split("=", 1)
        
        # Parsen mit SymPy-Transformationen (inkl. impliziter Multiplikation und ^ Support)
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
        
        transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
        
        lhs = parse_expr(lhs_str, transformations=transformations)
        rhs = parse_expr(rhs_str, transformations=transformations)
        
        # Gleichung formulieren: lhs - rhs = 0
        equation = sp.Eq(lhs, rhs)
        
        # Variablen identifizieren
        variables = equation.free_symbols
        
        if len(variables) == 0:
            raise HTTPException(status_code=400, detail="Keine Variable in der Gleichung gefunden.")
        if len(variables) > 1:
            vars_str = ", ".join(map(str, variables))
            raise HTTPException(status_code=400, detail=f"Mehrere Variablen gefunden: {vars_str}. Nur eine Variable wird unterstützt.")
        
        var = list(variables)[0]
        
        # Prüfung auf Linearität
        if not sp.degree(lhs - rhs, var) == 1:
             raise HTTPException(status_code=400, detail="Nur lineare Gleichungen werden unterstützt.")
        
        # Lösen
        solutions = sp.solve(equation, var)
        
        if not solutions:
            return {"result": "Keine Lösung"}
        
        # Ergebnis zurückgeben
        result = solutions[0]
            
        return {
            "variable": str(var),
            "solution": str(result),
            "numeric_solution": float(result.evalf())
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Ungültiges Gleichungsformat: {str(e)}")

@app.get("/api/health")
async def health():
    return {"status": "ok"}

# Lokales Serving der UI (wird auf Vercel durch vercel.json rewrites ersetzt)
if not IS_VERCEL:
    BASE_DIR = Path(__file__).resolve().parent.parent
    PUBLIC_DIR = BASE_DIR / "public"
    if PUBLIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(PUBLIC_DIR), html=True), name="public")
