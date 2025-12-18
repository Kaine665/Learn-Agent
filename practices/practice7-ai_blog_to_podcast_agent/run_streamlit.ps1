# 使用系统 Python 运行 Streamlit（因为虚拟环境无法安装 elevenlabs 包）
# 注意：需要先使用 pip install --user -r requirements.txt 安装依赖

# 查找系统 Python（排除虚拟环境）
$systemPython = $null

# 方法 1：尝试使用 py 命令（Python Launcher，Windows 推荐）
try {
    $pyOutput = py --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "使用 Python Launcher (py) 运行..." -ForegroundColor Green
        py -m streamlit run blog_to_podcast_agent.py
        exit $LASTEXITCODE
    }
} catch {
    # py 命令不可用，继续尝试其他方法
}

# 方法 2：查找系统 Python 路径
$pythonPaths = @(
    "C:\Python*\python.exe",
    "C:\Program Files\Python*\python.exe",
    "C:\Program Files (x86)\Python*\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
    "$env:APPDATA\Python\Python*\python.exe"
)

foreach ($pattern in $pythonPaths) {
    $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | 
             Where-Object { $_.FullName -notlike "*venv*" -and $_.FullName -notlike "*.venv*" } | 
             Select-Object -First 1
    if ($found) {
        $systemPython = $found.FullName
        break
    }
}

# 方法 3：从 PATH 中查找（排除虚拟环境）
if (-not $systemPython) {
    $allPythons = Get-Command python -All -ErrorAction SilentlyContinue
    foreach ($pythonCmd in $allPythons) {
        if ($pythonCmd.Source -notlike "*venv*" -and $pythonCmd.Source -notlike "*.venv*") {
            $systemPython = $pythonCmd.Source
            break
        }
    }
}

if ($systemPython) {
    Write-Host "使用系统 Python: $systemPython" -ForegroundColor Green
    & $systemPython -m streamlit run blog_to_podcast_agent.py
} else {
    Write-Host "错误: 找不到系统 Python" -ForegroundColor Red
    Write-Host "请尝试以下方法之一:" -ForegroundColor Yellow
    Write-Host "1. 退出虚拟环境后运行: deactivate" -ForegroundColor Yellow
    Write-Host "2. 使用完整路径运行系统 Python" -ForegroundColor Yellow
    Write-Host "3. 安装 Python Launcher 并使用: py -m streamlit run blog_to_podcast_agent.py" -ForegroundColor Yellow
    exit 1
}

