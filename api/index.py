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
        body { font-family: 'Outfit', sans-serif; background: radial-gradient(circle at top right, #1a1a2e, #16213e, #0f3460); min-height: 100vh; color: #e94560; margin: 0; display: flex; align-items: center; justify-content: center; }
        .glass { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }
        .input-glow:focus { box-shadow: 0 0 15px rgba(233, 69, 96, 0.5); border-color: #e94560; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .fade-in { animation: fadeIn 0.5s ease-out forwards; }
    </style>
</head>
<body class="p-4 sm:p-6 md:p-8">
    <div class="max-w-xl w-full glass p-6 sm:p-10 rounded-2xl sm:rounded-3xl shadow-2xl fade-in">
        <header class="text-center mb-8 sm:mb-12">
            <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold bg-gradient-to-r from-[#e94560] to-[#ff758c] bg-clip-text text-transparent mb-3">Gleichungslöser</h1>
            <p class="text-gray-400 font-light text-sm sm:base">Lineare Gleichungen mit einer Variablen sofort lösen.</p>
        </header>

        <div class="space-y-6">
            <div class="relative">
                <input type="text" id="equation" placeholder="z.B. 2x + 5 = 15" class="w-full bg-white/5 border border-white/10 rounded-xl sm:rounded-2xl py-4 px-5 sm:px-6 text-xl sm:text-2xl text-white outline-none transition-all input-glow placeholder:text-gray-600" autocomplete="off">
                <div class="hidden md:block absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 text-xs">Enter drücken</div>
            </div>

            <button id="solveBtn" class="w-full bg-gradient-to-r from-[#e94560] to-[#ff758c] text-white font-bold py-4 rounded-xl sm:rounded-2xl hover:scale-[1.01] active:scale-[0.99] transition-all shadow-lg shadow-pink-900/20 text-lg">Gleichung lösen</button>

            <div id="resultContainer" class="hidden glass rounded-xl sm:rounded-2xl p-5 sm:p-8 border-pink-500/20 transition-all duration-500">
                <div id="loading" class="hidden flex items-center justify-center space-x-2 py-4">
                    <div class="w-2.5 h-2.5 bg-pink-500 rounded-full animate-bounce"></div>
                    <div class="w-2.5 h-2.5 bg-pink-500 rounded-full animate-bounce delay-75"></div>
                    <div class="w-2.5 h-2.5 bg-pink-500 rounded-full animate-bounce delay-150"></div>
                </div>

                <div id="successContent" class="hidden text-center py-6 space-y-4">
                    <div id="resLine1" class="text-3xl sm:text-4xl md:text-5xl font-bold text-white break-all leading-tight"></div>
                    <div id="resLine2" class="text-xl sm:text-2xl md:text-3xl font-semibold text-pink-400 break-all leading-tight opacity-80"></div>
                </div>

                <div id="errorContent" class="hidden flex items-start space-x-3 text-red-400 bg-red-400/10 p-4 rounded-xl border border-red-400/20 text-sm sm:text-base">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                    <span id="errorMsg"></span>
                </div>
            </div>
        </div>

        <footer class="mt-10 sm:mt-16 text-center text-gray-500 text-[10px] sm:text-xs uppercase tracking-widest">
            Powered by SymPy Core & FastAPI
        </footer>
    </div>

    <script>
        const eqI = document.getElementById('equation');
        const sBtn = document.getElementById('solveBtn');
        const rC = document.getElementById('resultContainer');
        const ld = document.getElementById('loading');
        const sc = document.getElementById('successContent');
        const ec = document.getElementById('errorContent');
        
        const solve = async () => {
            const val = eqI.value.trim();
            if(!val) return;
            
            rC.classList.remove('hidden'); ld.classList.remove('hidden'); sc.classList.add('hidden'); ec.classList.add('hidden');
            
            try {
                const res = await fetch('/api/solve', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ equation: val })
                });
                const data = await res.json();
                ld.classList.add('hidden');
                
                if (res.ok) {
                    const variable = data.variable;
                    const fraction = data.solution;
                    const numeric = data.numeric_solution.toLocaleString('de-DE', {maximumFractionDigits: 4});
                    const periodic = data.periodic_solution;

                    let line1 = `${variable} = `;
                    let line2 = "";

                    if (periodic) {
                        line1 += periodic;
                        line2 = `${variable} = ${fraction}`;
                    } else if (fraction.includes('/')) {
                        line1 += numeric;
                        line2 = `${variable} = ${fraction}`;
                    } else {
                        line1 += fraction;
                        line2 = ""; // No second line needed for integers
                    }
                    
                    document.getElementById('resLine1').textContent = line1;
                    document.getElementById('resLine2').textContent = line2;
                    sc.classList.remove('hidden');
                } else {
                    document.getElementById('errorMsg').textContent = data.detail;
                    ec.classList.remove('hidden');
                }
            } catch {
                ld.classList.add('hidden');
                document.getElementById('errorMsg').textContent = 'Verbindungsfehler zum Server.';
                ec.classList.remove('hidden');
            }
        };

        sBtn.addEventListener('click', solve);
        eqI.addEventListener('keypress', (e) => { if(e.key === 'Enter') solve(); });
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
            vars_str = ", ".join(map(str, sorted(variables, key=lambda s: s.name)))
            raise HTTPException(status_code=400, detail=f"Mehrere Variablen gefunden: {vars_str}. Nur eine Variable wird unterstützt.")
        var = list(variables)[0]
        if not sp.degree(lhs - rhs, var) == 1:
             raise HTTPException(status_code=400, detail="Nur lineare Gleichungen unterstützt.")
        solutions = sp.solve(equation, var)
        if not solutions:
            return {"result": "Keine Lösung"}
        result = solutions[0]
        
        # Periodic decimal detection logic
        periodic_str = None
        if isinstance(result, sp.Rational) and not result.is_integer:
            p, q = result.p, result.q
            # Simple manual division to find period
            res = []
            rem_map = {}
            num = p % q
            while num != 0 and num not in rem_map:
                rem_map[num] = len(res)
                num *= 10
                res.append(str(num // q))
                num %= q
            
            whole = str(p // q)
            if num == 0:
                # Terminating decimal
                dec = "".join(res)
                periodic_str = f"{whole},{dec}" if dec else whole
            else:
                # Periodic decimal (German notation: dot above each periodic digit)
                loop_start = rem_map[num]
                non_periodic = "".join(res[:loop_start])
                periodic = "".join(res[loop_start:])
                # Append Unicode Combining Dot Above (\u0307) to each digit in the period
                periodic_dotted = "".join([f"{d}\u0307" for d in periodic])
                periodic_str = f"{whole},{non_periodic}{periodic_dotted}"

        return {
            "variable": str(var),
            "solution": str(result),
            "numeric_solution": float(result.evalf()),
            "periodic_solution": periodic_str
        }
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=400, detail=f"Ungültige Gleichung.")

@app.get("/api/health")
async def health():
    return {"status": "ok"}
