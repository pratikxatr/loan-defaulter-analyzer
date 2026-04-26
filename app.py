from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


def calculate_emi(principal, annual_rate, months):
    if annual_rate == 0:
        return principal / months
    r = annual_rate / 12 / 100
    emi = principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    return emi


def assess_risk(data):
    income        = data['income']
    employment    = data['employment']
    job_years     = data['job_years']
    loan_amount   = data['loan_amount']
    tenure        = data['tenure']
    rate          = data['rate']
    existing_emi  = data['existing_emi']
    credit_score  = data['credit_score']
    prev_defaults = data['prev_defaults']

    new_emi    = calculate_emi(loan_amount, rate, tenure)
    total_emi  = new_emi + existing_emi
    dti        = (total_emi / income) * 100
    lti        = loan_amount / (income * 12)

    risk_score = 0
    factors    = []

    # DTI
    if dti <= 30:
        factors.append({"type": "ok",   "msg": f"Debt-to-income {dti:.1f}% — healthy (≤30%)"})
    elif dti <= 50:
        risk_score += 2
        factors.append({"type": "warn", "msg": f"Debt-to-income {dti:.1f}% — moderate (30–50%)"})
    else:
        risk_score += 4
        factors.append({"type": "bad",  "msg": f"Debt-to-income {dti:.1f}% — high risk (>50%)"})

    # Credit score
    if credit_score >= 750:
        factors.append({"type": "ok",   "msg": f"Credit score {int(credit_score)} — excellent"})
    elif credit_score >= 600:
        risk_score += 2
        factors.append({"type": "warn", "msg": f"Credit score {int(credit_score)} — fair"})
    else:
        risk_score += 4
        factors.append({"type": "bad",  "msg": f"Credit score {int(credit_score)} — poor"})

    # Employment
    emp_labels = {"salaried": "Salaried", "self": "Self-employed",
                  "business": "Business owner", "unemployed": "Unemployed"}
    emp_name = emp_labels.get(employment, employment)
    if employment == "salaried":
        factors.append({"type": "ok",   "msg": f"{emp_name} — stable income"})
    elif employment in ("self", "business"):
        risk_score += 1
        factors.append({"type": "warn", "msg": f"{emp_name} — variable income"})
    else:
        risk_score += 5
        factors.append({"type": "bad",  "msg": f"{emp_name} — high default risk"})

    # Job stability
    if job_years >= 3:
        factors.append({"type": "ok",   "msg": f"{job_years:.0f} years in role — stable"})
    elif job_years >= 1:
        risk_score += 1
        factors.append({"type": "warn", "msg": f"{job_years:.0f} year(s) in role — somewhat new"})
    else:
        risk_score += 2
        factors.append({"type": "bad",  "msg": "Under 1 year in role — instability risk"})

    # Loan-to-income
    if lti <= 5:
        factors.append({"type": "ok",   "msg": f"Loan is {lti:.1f}× annual income — manageable"})
    elif lti <= 10:
        risk_score += 2
        factors.append({"type": "warn", "msg": f"Loan is {lti:.1f}× annual income — high leverage"})
    else:
        risk_score += 3
        factors.append({"type": "bad",  "msg": f"Loan is {lti:.1f}× annual income — very high"})

    # Previous defaults
    if prev_defaults == 0:
        factors.append({"type": "ok",   "msg": "No previous loan defaults"})
    elif prev_defaults == 1:
        risk_score += 3
        factors.append({"type": "warn", "msg": "1 previous default — concern raised"})
    else:
        risk_score += 5
        factors.append({"type": "bad",  "msg": f"{int(prev_defaults)} previous defaults — red flag"})

    max_score = 19
    if risk_score <= 3:
        tier = "low"
    elif risk_score <= 8:
        tier = "moderate"
    else:
        tier = "high"

    return {
        "risk_score": risk_score,
        "max_score":  max_score,
        "tier":       tier,
        "new_emi":    round(new_emi, 2),
        "total_emi":  round(total_emi, 2),
        "dti":        round(dti, 2),
        "lti":        round(lti, 2),
        "factors":    factors,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/assess", methods=["POST"])
def assess():
    body = request.get_json()
    required = ["income", "employment", "job_years", "loan_amount",
                "tenure", "rate", "existing_emi", "credit_score", "prev_defaults"]

    for field in required:
        if field not in body:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        data = {
            "income":        float(body["income"]),
            "employment":    str(body["employment"]),
            "job_years":     float(body["job_years"]),
            "loan_amount":   float(body["loan_amount"]),
            "tenure":        float(body["tenure"]),
            "rate":          float(body["rate"]),
            "existing_emi":  float(body["existing_emi"]),
            "credit_score":  float(body["credit_score"]),
            "prev_defaults": int(body["prev_defaults"]),
        }

        if data["income"] <= 0 or data["loan_amount"] <= 0 or data["tenure"] <= 0:
            return jsonify({"error": "Income, loan amount, and tenure must be greater than 0"}), 400

        result = assess_risk(data)
        return jsonify(result)

    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
