from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sympy as sp
import os

# App-Instanz
app = FastAPI()

class EquationRequest(BaseModel):
    equation: str

@app.post("/api/solve")
async def solve_equation(request: EquationRequest):
    eq_str = request.equation.replace(" ", "")
    
    if "=" not in eq_str:
        raise HTTPException(status_code=400, detail="Die Gleichung muss ein '=' Zeichen enthalten.")
    
    try:
        lhs_str, rhs_str = eq_str.split("=", 1)
        
        # SymPy Parser Transformationen (inkl. impliziter Multiplikation und ^ Support)
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
        transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
        
        lhs = parse_expr(lhs_str, transformations=transformations)
        rhs = parse_expr(rhs_str, transformations=transformations)
        
        equation = sp.Eq(lhs, rhs)
        variables = equation.free_symbols
        
        if len(variables) == 0:
            raise HTTPException(status_code=400, detail="Keine Variable in der Gleichung gefunden.")
        if len(variables) > 1:
            vars_str = ", ".join(map(str, variables))
            raise HTTPException(status_code=400, detail=f"Mehrere Variablen gefunden: {vars_str}. Nur eine Variable wird unterstützt.")
        
        var = list(variables)[0]
        
        if not sp.degree(lhs - rhs, var) == 1:
             raise HTTPException(status_code=400, detail="Nur lineare Gleichungen werden unterstützt.")
        
        solutions = sp.solve(equation, var)
        
        if not solutions:
            return {"result": "Keine Lösung"}
        
        result = solutions[0]
            
        return {
            "variable": str(var),
            "solution": str(result),
            "numeric_solution": float(result.evalf())
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Fehler: {str(e)}")

@app.get("/api/health")
async def health():
    return {"status": "ok"}
