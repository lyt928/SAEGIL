param(
    [ValidateSet("dev", "demo", "real")]
    [string]$Mode = "dev",

    [ValidateSet("mock", "real")]
    [string]$DetectorMode = "real",

    [string]$MockScenario = "zone_intrusion_missing_ppe",

    [int]$Port = 8000
)

if ($Mode -eq "demo" -and $PSBoundParameters.ContainsKey("DetectorMode") -eq $false) {
    $DetectorMode = "mock"
}

if ($Mode -eq "real") {
    $DetectorMode = "real"
}

$env:RUN_MODE = $Mode
$env:DETECTOR_MODE = $DetectorMode
$env:MOCK_SCENARIO = $MockScenario

python -m uvicorn apps.backend.main:app --reload --host 0.0.0.0 --port $Port
