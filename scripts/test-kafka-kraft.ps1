# Script de test pour vérifier le fonctionnement de Kafka en mode KRaft
# Ce script teste la connectivité, la production et la consommation de messages

param(
    [string]$KafkaBootstrapServer = "localhost:9092",
    [string]$TestTopic = "test-kraft-topic"
)

Write-Host "🧪 Test de Kafka en mode KRaft..." -ForegroundColor Green
Write-Host "📡 Serveur Kafka: $KafkaBootstrapServer" -ForegroundColor Cyan
Write-Host "📝 Topic de test: $TestTopic" -ForegroundColor Cyan

# Fonction pour tester la connectivité
function Test-KafkaConnectivity {
    Write-Host "`n🔌 Test de connectivité..." -ForegroundColor Yellow
    try {
        $result = docker exec kafka kafka-broker-api-versions --bootstrap-server $KafkaBootstrapServer 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Connectivité Kafka OK" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Erreur de connectivité Kafka" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Erreur lors du test de connectivité: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Fonction pour créer le topic de test
function New-TestTopic {
    Write-Host "`n📝 Création du topic de test..." -ForegroundColor Yellow
    try {
        docker exec kafka kafka-topics --bootstrap-server $KafkaBootstrapServer --create --topic $TestTopic --partitions 1 --replication-factor 1 --if-not-exists
        Write-Host "✅ Topic de test créé avec succès" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Erreur lors de la création du topic: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Fonction pour produire un message de test
function Send-TestMessage {
    param([string]$Message)
    
    Write-Host "`n📤 Envoi d'un message de test..." -ForegroundColor Yellow
    try {
        $Message | docker exec -i kafka kafka-console-producer --bootstrap-server $KafkaBootstrapServer --topic $TestTopic
        Write-Host "✅ Message envoyé avec succès" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Erreur lors de l'envoi du message: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Fonction pour consommer des messages
function Receive-TestMessages {
    param([int]$TimeoutSeconds = 10)
    
    Write-Host "`n📥 Consommation des messages (timeout: ${TimeoutSeconds}s)..." -ForegroundColor Yellow
    try {
        $job = Start-Job -ScriptBlock {
            param($Server, $Topic, $Timeout)
            docker exec kafka kafka-console-consumer --bootstrap-server $Server --topic $Topic --from-beginning --timeout-ms ($Timeout * 1000)
        } -ArgumentList $KafkaBootstrapServer, $TestTopic, $TimeoutSeconds
        
        $result = Wait-Job $job -Timeout ($TimeoutSeconds + 5)
        $output = Receive-Job $job
        Remove-Job $job
        
        if ($output) {
            Write-Host "✅ Messages reçus:" -ForegroundColor Green
            $output | ForEach-Object { Write-Host "  📨 $_" -ForegroundColor Cyan }
            return $true
        } else {
            Write-Host "⚠️ Aucun message reçu dans le délai imparti" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ Erreur lors de la consommation des messages: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Fonction pour nettoyer le topic de test
function Remove-TestTopic {
    Write-Host "`n🧹 Nettoyage du topic de test..." -ForegroundColor Yellow
    try {
        docker exec kafka kafka-topics --bootstrap-server $KafkaBootstrapServer --delete --topic $TestTopic
        Write-Host "✅ Topic de test supprimé" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Impossible de supprimer le topic de test: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Exécution des tests
Write-Host "`n🚀 Démarrage des tests Kafka KRaft..." -ForegroundColor Green

$testResults = @()

# Test 1: Connectivité
$connectivityTest = Test-KafkaConnectivity
$testResults += @{Name="Connectivité"; Result=$connectivityTest}

if (-not $connectivityTest) {
    Write-Host "`n❌ Test de connectivité échoué. Arrêt des tests." -ForegroundColor Red
    exit 1
}

# Test 2: Création de topic
$topicCreationTest = New-TestTopic
$testResults += @{Name="Création de topic"; Result=$topicCreationTest}

if (-not $topicCreationTest) {
    Write-Host "`n❌ Création de topic échouée. Arrêt des tests." -ForegroundColor Red
    exit 1
}

# Test 3: Production de message
$testMessage = "Test message from PowerShell at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$messageSendTest = Send-TestMessage -Message $testMessage
$testResults += @{Name="Production de message"; Result=$messageSendTest}

# Test 4: Consommation de message
$messageReceiveTest = Receive-TestMessages -TimeoutSeconds 10
$testResults += @{Name="Consommation de message"; Result=$messageReceiveTest}

# Nettoyage
Remove-TestTopic

# Résumé des tests
Write-Host "`n📊 Résumé des tests:" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green

$passedTests = 0
$totalTests = $testResults.Count

foreach ($test in $testResults) {
    $status = if ($test.Result) { "✅ PASS" } else { "❌ FAIL" }
    $color = if ($test.Result) { "Green" } else { "Red" }
    Write-Host "  $($test.Name): $status" -ForegroundColor $color
    if ($test.Result) { $passedTests++ }
}

Write-Host "`n📈 Résultat global: $passedTests/$totalTests tests réussis" -ForegroundColor $(if ($passedTests -eq $totalTests) { "Green" } else { "Yellow" })

if ($passedTests -eq $totalTests) {
    Write-Host "`n🎉 Tous les tests Kafka KRaft ont réussi!" -ForegroundColor Green
    Write-Host "Kafka fonctionne correctement en mode KRaft." -ForegroundColor Green
} else {
    Write-Host "`n⚠️ Certains tests ont échoué. Vérifiez la configuration Kafka." -ForegroundColor Yellow
}
