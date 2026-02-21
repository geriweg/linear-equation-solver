from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sympy as sp
import os

app = FastAPI()

# HTML Inhalt direkt einbetten für maximale Zuverlässigkeit auf Vercel
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gleichungslöser | Premium-Mathe-Tool</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Outfit', sans-serif; background: radial-gradient(circle at top right, #1a1a2e, #16213e, #0f3460); min-height: 100vh; color: #e94560; }
        .glass { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }
        .input-glow:focus { box-shadow: 0 0 15px rgba(233, 69, 96, 0.5); border-color: #e94560; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .fade-in { animation: fadeIn 0.5s ease-out forwards; }
    </style>
</head>
<body class="flex items-center justify-center p-4">
    <div class="max-w-2xl w-full glass p-8 rounded-3xl shadow-2xl fade-in">
        <header class="text-center mb-10">
            <h1 class="text-4xl font-bold bg-gradient-to-r from-[#e94560] to-[#ff758c] bg-clip-text text-transparent mb-2">Gleichungslöser</h1>
            <p class="text-gray-400 font-light">Geben Sie Ihre lineare Gleichung ein (z. B. <span class="text-pink-400 italic">2x + 5 = 15</span>)</p>
        </header>
        <div class="space-y-6">
            <div class="relative">
                <input type="text" id="equation" placeholder="2x + 5 = 15" class="w-full bg-white/5 border border-white/10 rounded-2xl py-4 px-6 text-2xl text-white outline-none transition-all input-glow" autocomplete="off">
                <div class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 text-sm">Eingabetaste drücken</div>
            </div>
            <button id="solveBtn" class="w-full bg-gradient-to-r from-[#e94560] to-[#ff758c] text-white font-bold py-4 rounded-2xl hover:scale-[1.02] active:scale-[0.98] transition-all shadow-lg shadow-pink-900/20">Gleichung lösen</button>
            <div id="resultContainer" class="hidden glass rounded-2xl p-6 border-pink-500/20 transition-all duration-500">
                <div id="loading" class="hidden flex items-center justify-center space-x-2 py-4">
                    <div class="w-3 h-3 bg-pink-500 rounded-full animate-bounce"></div>
                    <div class="w-3 h-3 bg-pink-500 rounded-full animate-bounce delay-75"></div>
                    <div class="w-3 h-3 bg-pink-500 rounded-full animate-bounce delay-150"></div>
                </div>
                <div id="successContent" class="hidden text-center">
                    <p class="text-gray-400 text-sm uppercase tracking-widest mb-1">Ergebnis für <span id="resVar" class="text-pink-400">x</span></p>
                    <div id="resVal" class="text-5xl font-bold text-white mb-2">0</div>
                    <p id="resNumeric" class="text-gray-500 text-sm"></p>
                </div>
                <div id="errorContent" class="hidden flex items-start space-x-3 text-red-400 bg-red-400/10 p-4 rounded-xl border border-red-400/20">
                    <span id="errorMsg">Etwas ist schiefgelaufen.</span>
                </div>
            </div>
        </div>
        <footer class="mt-10 text-center text-gray-500 text-xs">Unterstützt durch SymPy & FastAPI</footer>
    </div>
    <script>
        const eqInput = document.getElementById('equation');
        const solveBtn = document.getElementById('solveBtn');
        const resCont = document.getElementById('resultContainer');
        const load = document.getElementById('loading');
        const succ = document.getElementById('successContent');
        const err = document.getElementById('errorContent');
        const solve = async () => {
            const eq = eqInput.value.trim();
            if (!eq) return;
            resCont.classList.remove('hidden'); load.classList.remove('hidden'); succ.classList.add('hidden'); err.classList.add('hidden');
            try {
                const r = await fetch('/api/solve', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ equation: eq }) });
                const d = await r.json();
                load.classList.add('hidden');
                if (r.ok) {
                    document.getElementById('resVar').textContent = d.variable;
                    document.getElementById('resVal').textContent = d.solution;
                    document.getElementById('resNumeric').textContent = `Dezimal: ${d.numeric_solution.toFixed(4)}`;
                    succ.classList.remove('hidden');
                } else {
                    document.getElementById('errorMsg').textContent = d.detail || 'Fehler.';
                    err.classList.remove('hidden');
                }
            } catch { load.classList.add('hidden'); document.getElementById('errorMsg').textContent = 'Netzwerkfehler.'; err.classList.remove('hidden'); }
        };
        solveBtn.addEventListener('click', solve);
        eqInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') solve(); });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return HTML_CONTENT

class EquationRequest(BaseModel):
    equation: str

@app.post("/api/solve")
async def solve_equation(request: EquationRequest):
    eq_str = request.equation.replace(" ", "")
    if "=" not in eq_str:
        raise HTTPException(status_code=400, detail="Die Gleichung muss ein '=' Zeichen enthalten.")
    try:
        lhs_str, rhs_str = eq_str.split("=", 1)
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
        transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
        lhs = parse_expr(lhs_str, transformations=transformations)
        rhs = parse_expr(rhs_str, transformations=transformations)
        equation = sp.Eq(lhs, rhs)
        variables = equation.free_symbols
        if len(variables) == 0:
            raise HTTPException(status_code=400, detail="Keine Variable gefunden.")
        if len(variables) > 1:
            raise HTTPException(status_code=400, detail=f"Nur eine Variable unterstützt.")
        var = list(variables)[0]
        if not sp.degree(lhs - rhs, var) == 1:
             raise HTTPException(status_code=400, detail="Nur lineare Gleichungen unterstützt.")
        solutions = sp.solve(equation, var)
        if not solutions:
            return {"result": "Keine Lösung"}
        result = solutions[0]
        return {"variable": str(var), "solution": str(result), "numeric_solution": float(result.evalf())}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=400, detail=f"Ungültige Gleichung.")

@app.get("/api/health")
async def health():
    return {"status": "ok"}
