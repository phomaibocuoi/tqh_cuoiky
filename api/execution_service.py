import pandas as pd
import plotly.graph_objects as go
import contextlib
import io
import traceback
from pydantic import BaseModel

class ExecutionRequest(BaseModel):
    code: str
    data_json: str 

def execute_code_safely(code: str, df: pd.DataFrame) -> dict:
    import plotly.express as px
    import numpy as np
    
    env = {
        "pd": pd,
        "go": go,
        "px": px,
        "np": np,
        "__builtins__": __builtins__,
        "df": df.copy()
    }
    
    output_buffer = io.StringIO()
    
    try:
        with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
            exec(code, env)
            
        logs = output_buffer.getvalue()
        
        result = {
            "status": "success",
            "logs": logs,
            "has_fig": False,
            "has_df": False
        }
        
        if "fig" in env:
            fig = env["fig"]
            result["has_fig"] = True
            result["fig_json"] = fig.to_json()
            
        if "result_df" in env:
            res_df = env["result_df"]
            if isinstance(res_df, pd.DataFrame):
                result["has_df"] = True
                result["df_json"] = res_df.to_json(orient="records")
                
        if "insight" in env:
            result["insight"] = str(env["insight"])
            
        return result
        
    except Exception as e:
        error_msg = traceback.format_exc()
        return {
            "status": "error",
            "error_msg": str(e),
            "traceback": error_msg
        }
