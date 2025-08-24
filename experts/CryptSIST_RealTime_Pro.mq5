//+------------------------------------------------------------------+
//|                                        CryptSIST_RealTime_Pro.mq5 |
//|                                    CryptSIST Development Team     |
//|                                             https://cryptsist.com |
//+------------------------------------------------------------------+
#property copyright "CryptSIST Development Team"
#property link      "https://cryptsist.com"
#property version   "3.00"
#property strict

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\OrderInfo.mqh>
#include <Trade\HistoryOrderInfo.mqh>
#include <Trade\DealInfo.mqh>

//+------------------------------------------------------------------+
//| Signal type enumeration                                          |
//+------------------------------------------------------------------+
enum ENUM_SIGNAL_TYPE
{
    SIGNAL_NONE = 0,
    SIGNAL_BUY = 1,
    SIGNAL_SELL = 2,
    SIGNAL_HOLD = 3
};

//+------------------------------------------------------------------+
//| Analysis strength enumeration                                    |
//+------------------------------------------------------------------+
enum ENUM_SIGNAL_STRENGTH
{
    STRENGTH_WEAK = 1,
    STRENGTH_MODERATE = 2,
    STRENGTH_STRONG = 3,
    STRENGTH_VERY_STRONG = 4
};

//--- Input parameters
input group "=== 🚀 CryptSIST Real-Time Settings ==="
input string ServerURL = "http://127.0.0.1:8000";       // CryptSIST Server URL
input string APIKey = "";                                // API Key (optional)
input int RequestTimeout = 3000;                         // Request timeout (ms)
input bool EnableInstantAnalysis = true;                 // Enable instant tick analysis
input int AnalysisIntervalMS = 500;                      // Analysis interval (milliseconds)

input group "=== 💰 Trading Configuration ==="
input double LotSize = 0.01;                            // Lot size
input double MaxRiskPercent = 1.5;                      // Maximum risk per trade (%)
input int MaxDailyTrades = 15;                          // Maximum trades per day
input bool EnableAutoTrading = false;                   // Enable automatic trading
input double MinConfidenceLevel = 0.75;                 // Minimum confidence to trade
input bool OnlyHighConfidenceTrades = true;             // Only trade high confidence signals

input group "=== ⚡ Real-Time Display ==="
input bool ShowLiveAnalysis = true;                     // Show live analysis on chart
input bool ShowSignalArrows = true;                     // Show instant signal arrows
input bool ShowConfidenceBar = true;                    // Show confidence level bar
input bool ShowMarketSentiment = true;                  // Show market sentiment
input bool EnableSoundAlerts = true;                    // Enable sound alerts
input bool EnablePushNotifications = false;             // Enable push notifications

input group "=== 🛡️ Advanced Risk Management ==="
input double StopLossPoints = 300;                      // Stop Loss in points
input double TakeProfitPoints = 600;                    // Take Profit in points
input bool UseTrailingStop = true;                      // Use trailing stop
input double TrailingStopPoints = 200;                  // Trailing stop distance
input bool UseBreakEven = true;                         // Move SL to breakeven
input double BreakEvenPoints = 100;                     // Breakeven trigger points

input group "=== 📊 Visual Dashboard ==="
input int DashboardX = 20;                              // Dashboard X position
input int DashboardY = 50;                              // Dashboard Y position
input color DashboardBgColor = clrDarkBlue;             // Dashboard background
input color BuySignalColor = clrLime;                   // Buy signal color
input color SellSignalColor = clrRed;                   // Sell signal color
input color HoldSignalColor = clrYellow;                // Hold signal color
input int SignalArrowSize = 4;                          // Signal arrow size

//--- Global variables
CTrade trade;
CPositionInfo position;
COrderInfo order;

// Real-time analysis variables
datetime lastAnalysisTime = 0;
datetime lastSignalTime = 0;
datetime lastTradeTime = 0;
int dailyTradeCount = 0;
datetime lastTradeDate = 0;

// Current market state
ENUM_SIGNAL_TYPE currentSignal = SIGNAL_NONE;
ENUM_SIGNAL_TYPE lastSignal = SIGNAL_NONE;
double currentConfidence = 0.0;
double lastConfidence = 0.0;
string currentAnalysis = "";
double currentPrice = 0.0;
string marketSentiment = "NEUTRAL";
double sentimentScore = 0.0;

// Performance tracking
int totalTrades = 0;
int winningTrades = 0;
double totalProfit = 0.0;
double maxDrawdown = 0.0;
double currentDrawdown = 0.0;
double initialBalance = 0.0;

// Dashboard objects
string dashboardPrefix = "CryptSIST_Dashboard_";
string signalPrefix = "CryptSIST_Signal_";
string analysisPrefix = "CryptSIST_Analysis_";

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("🚀 CryptSIST Real-Time Pro EA v3.0 Starting...");
    Print("⚡ Instant Analysis: ", EnableInstantAnalysis ? "ENABLED" : "DISABLED");
    Print("🎯 Analysis Interval: ", AnalysisIntervalMS, "ms");
    Print("💰 Auto Trading: ", EnableAutoTrading ? "ENABLED" : "DISABLED");
    
    // Initialize trade class
    trade.SetExpertMagicNumber(123456);
    trade.SetDeviationInPoints(10);
    trade.SetTypeFilling(ORDER_FILLING_FOK);
    
    // Get initial balance
    initialBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    
    // Reset daily counter
    CheckNewDay();
    
    // Create dashboard
    if(ShowLiveAnalysis)
        CreateLiveDashboard();
    
    // Test connection
    TestServerConnection();
    
    Print("✅ CryptSIST Real-Time Pro EA initialized successfully!");
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    // Clean up all objects
    CleanupAllObjects();
    
    Print("📊 Final Statistics:");
    Print("💰 Total Trades: ", totalTrades);
    Print("✅ Winning Trades: ", winningTrades);
    Print("📈 Win Rate: ", totalTrades > 0 ? DoubleToString((double)winningTrades/totalTrades*100, 2) : "0", "%");
    Print("💵 Total Profit: $", DoubleToString(totalProfit, 2));
    Print("📉 Max Drawdown: ", DoubleToString(maxDrawdown, 2), "%");
    
    Print("👋 CryptSIST Real-Time Pro EA stopped!");
}

//+------------------------------------------------------------------+
//| Expert tick function - REAL-TIME ANALYSIS                       |
//+------------------------------------------------------------------+
void OnTick()
{
    // Get current market data
    currentPrice = SymbolInfoDouble(Symbol(), SYMBOL_BID);
    
    // Check if enough time passed for new analysis
    if(EnableInstantAnalysis)
    {
        if(GetTickCount() - lastAnalysisTime > AnalysisIntervalMS)
        {
            PerformRealTimeAnalysis();
            lastAnalysisTime = GetTickCount();
        }
    }
    
    // Update dashboard every tick
    if(ShowLiveAnalysis)
        UpdateLiveDashboard();
    
    // Monitor existing trades
    MonitorActiveTrades();
    
    // Execute trading logic
    if(EnableAutoTrading)
        ExecuteTradingLogic();
}

//+------------------------------------------------------------------+
//| Perform real-time market analysis                                |
//+------------------------------------------------------------------+
void PerformRealTimeAnalysis()
{
    // Get latest market data
    MqlRates rates[];
    if(CopyRates(Symbol(), PERIOD_CURRENT, 0, 50, rates) < 50)
        return;
    
    // Store previous signal
    lastSignal = currentSignal;
    lastConfidence = currentConfidence;
    
    // Get CryptSIST analysis
    GetCryptSISTAnalysis();
    
    // Perform technical analysis backup
    PerformTechnicalAnalysis(rates);
    
    // Combine analysis results
    CombineAnalysisResults();
    
    // Check for signal change
    if(currentSignal != lastSignal || MathAbs(currentConfidence - lastConfidence) > 0.1)
    {
        // New signal detected
        ProcessNewSignal();
    }
    
    lastSignalTime = TimeCurrent();
}

//+------------------------------------------------------------------+
//| Get analysis from CryptSIST server                               |
//+------------------------------------------------------------------+
void GetCryptSISTAnalysis()
{
    string url = ServerURL + "/signal/" + Symbol();
    string response = HttpRequest(url);
    
    Print("🔍 Requesting: ", url);
    Print("📥 Response: ", StringLen(response) > 0 ? response : "NO RESPONSE");
    
    if(StringLen(response) > 0)
    {
        ParseCryptSISTResponse(response);
    }
    else
    {
        // Fallback to technical analysis only
        currentAnalysis = "🔧 Technical Analysis Only";
        Print("⚠️ Using fallback technical analysis");
    }
}

//+------------------------------------------------------------------+
//| Parse CryptSIST server response                                  |
//+------------------------------------------------------------------+
void ParseCryptSISTResponse(string response)
{
    Print("🔍 Parsing response: ", response);
    
    // Simple JSON parsing (in production, use proper JSON library)
    if(StringFind(response, "\"signal\":\"BUY\"") >= 0)
    {
        currentSignal = SIGNAL_BUY;
        currentAnalysis = "🟢 CryptSIST: STRONG BUY";
        Print("📊 Signal parsed: BUY");
    }
    else if(StringFind(response, "\"signal\":\"SELL\"") >= 0)
    {
        currentSignal = SIGNAL_SELL;
        currentAnalysis = "🔴 CryptSIST: STRONG SELL";
        Print("📊 Signal parsed: SELL");
    }
    else if(StringFind(response, "\"signal\":\"HOLD\"") >= 0)
    {
        currentSignal = SIGNAL_HOLD;
        currentAnalysis = "🟡 CryptSIST: HOLD";
        Print("📊 Signal parsed: HOLD");
    }
    else
    {
        currentSignal = SIGNAL_NONE;
        currentAnalysis = "⚪ CryptSIST: NO SIGNAL";
        Print("📊 Signal parsed: NONE");
    }
    
    // Extract confidence
    int confStart = StringFind(response, "\"confidence\":");
    if(confStart >= 0)
    {
        string confStr = StringSubstr(response, confStart + 13, 5);
        currentConfidence = StringToDouble(confStr);
        Print("📊 Confidence: ", currentConfidence);
    }
    else
    {
        currentConfidence = 0.5; // Default confidence
        Print("📊 Using default confidence: ", currentConfidence);
    }
    
    // Extract sentiment
    if(StringFind(response, "\"sentiment\":\"BULLISH\"") >= 0)
    {
        marketSentiment = "BULLISH";
        sentimentScore = 0.8;
    }
    else if(StringFind(response, "\"sentiment\":\"BEARISH\"") >= 0)
    {
        marketSentiment = "BEARISH";
        sentimentScore = -0.8;
    }
    else
    {
        marketSentiment = "NEUTRAL";
        sentimentScore = 0.0;
    }
}

//+------------------------------------------------------------------+
//| Perform technical analysis as backup                             |
//+------------------------------------------------------------------+
void PerformTechnicalAnalysis(const MqlRates &rates[])
{
    if(ArraySize(rates) < 20) return;
    
    // Calculate moving averages
    double ma20 = CalculateMA(rates, 20);
    double ma50 = CalculateMA(rates, 50);
    
    // Calculate RSI
    double rsi = CalculateRSI(rates, 14);
    
    // Calculate MACD
    double macd[], signal[], histogram[];
    CalculateMACD(rates, macd, signal, histogram);
    
    // Technical signal logic
    ENUM_SIGNAL_TYPE techSignal = SIGNAL_NONE;
    double techConfidence = 0.0;
    
    // Check if we have enough MACD data
    bool hasMACD = ArraySize(macd) >= 2 && ArraySize(signal) >= 2;
    
    // MA Cross strategy
    if(currentPrice > ma20 && ma20 > ma50 && rsi > 30 && rsi < 70)
    {
        if(hasMACD && macd[0] > signal[0] && macd[1] <= signal[1])
        {
            techSignal = SIGNAL_BUY;
            techConfidence = 0.7;
        }
    }
    else if(currentPrice < ma20 && ma20 < ma50 && rsi > 30 && rsi < 70)
    {
        if(hasMACD && macd[0] < signal[0] && macd[1] >= signal[1])
        {
            techSignal = SIGNAL_SELL;
            techConfidence = 0.7;
        }
    }
    else
    {
        techSignal = SIGNAL_HOLD;
        techConfidence = 0.5;
    }
    
    // If no CryptSIST signal, use technical
    if(currentSignal == SIGNAL_NONE)
    {
        currentSignal = techSignal;
        currentConfidence = techConfidence;
        currentAnalysis = "🔧 Technical: " + EnumToString(techSignal);
    }
}

//+------------------------------------------------------------------+
//| Combine different analysis results                               |
//+------------------------------------------------------------------+
void CombineAnalysisResults()
{
    // Adjust confidence based on market conditions
    if(marketSentiment == "BULLISH" && currentSignal == SIGNAL_BUY)
        currentConfidence = MathMin(1.0, currentConfidence + 0.1);
    else if(marketSentiment == "BEARISH" && currentSignal == SIGNAL_SELL)
        currentConfidence = MathMin(1.0, currentConfidence + 0.1);
    
    // Add volatility adjustment
    double atr = CalculateATR(14);
    if(atr > SymbolInfoDouble(Symbol(), SYMBOL_POINT) * 1000)
    {
        currentConfidence = MathMax(0.0, currentConfidence - 0.15); // Reduce confidence in high volatility
    }
}

//+------------------------------------------------------------------+
//| Process new signal detection                                     |
//+------------------------------------------------------------------+
void ProcessNewSignal()
{
    // Show signal on chart
    if(ShowSignalArrows)
        ShowSignalArrow();
    
    // Play sound alert
    if(EnableSoundAlerts)
        PlaySignalSound();
    
    // Send push notification
    if(EnablePushNotifications)
        SendPushNotification();
    
    // Update analysis text
    string signalText = StringFormat("🎯 %s | Confidence: %.1f%% | %s", 
                                     EnumToString(currentSignal), 
                                     currentConfidence * 100, 
                                     marketSentiment);
    
    Print("⚡ NEW SIGNAL: ", signalText);
    
    // Log signal
    LogSignalToFile();
}

//+------------------------------------------------------------------+
//| Execute trading logic based on signals                           |
//+------------------------------------------------------------------+
void ExecuteTradingLogic()
{
    // Check if auto trading is actually enabled in MT5
    bool isAutoTradingEnabled = TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) && 
                                MQLInfoInteger(MQL_TRADE_ALLOWED) && 
                                AccountInfoInteger(ACCOUNT_TRADE_EXPERT) &&
                                EnableAutoTrading; // Also check EA parameter
    
    if(!isAutoTradingEnabled)
        return;
        
    // Check daily trade limit
    if(dailyTradeCount >= MaxDailyTrades)
        return;
    
    // Check minimum confidence
    if(currentConfidence < MinConfidenceLevel)
        return;
    
    // Check if we already have a position
    if(PositionsTotal() > 0)
        return;
    
    // Check time since last trade (avoid overtrading)
    if(TimeCurrent() - lastTradeTime < 300) // 5 minutes minimum
        return;
    
    // Execute trade based on signal
    if(currentSignal == SIGNAL_BUY && currentConfidence >= MinConfidenceLevel)
    {
        if(OnlyHighConfidenceTrades && currentConfidence < 0.8)
            return;
            
        ExecuteBuyOrder();
    }
    else if(currentSignal == SIGNAL_SELL && currentConfidence >= MinConfidenceLevel)
    {
        if(OnlyHighConfidenceTrades && currentConfidence < 0.8)
            return;
            
        ExecuteSellOrder();
    }
}

//+------------------------------------------------------------------+
//| Execute buy order                                                |
//+------------------------------------------------------------------+
void ExecuteBuyOrder()
{
    double ask = SymbolInfoDouble(Symbol(), SYMBOL_ASK);
    double sl = ask - StopLossPoints * SymbolInfoDouble(Symbol(), SYMBOL_POINT);
    double tp = ask + TakeProfitPoints * SymbolInfoDouble(Symbol(), SYMBOL_POINT);
    
    if(trade.Buy(LotSize, Symbol(), ask, sl, tp, 
                 StringFormat("CryptSIST BUY %.1f%%", currentConfidence * 100)))
    {
        lastTradeTime = TimeCurrent();
        dailyTradeCount++;
        totalTrades++;
        
        Print("✅ BUY ORDER EXECUTED");
        Print("💰 Price: ", ask);
        Print("🛡️ Stop Loss: ", sl);
        Print("🎯 Take Profit: ", tp);
        Print("📊 Confidence: ", DoubleToString(currentConfidence * 100, 1), "%");
    }
    else
    {
        Print("❌ BUY ORDER FAILED: ", trade.ResultRetcode(), " - ", trade.ResultRetcodeDescription());
    }
}

//+------------------------------------------------------------------+
//| Execute sell order                                               |
//+------------------------------------------------------------------+
void ExecuteSellOrder()
{
    double bid = SymbolInfoDouble(Symbol(), SYMBOL_BID);
    double sl = bid + StopLossPoints * SymbolInfoDouble(Symbol(), SYMBOL_POINT);
    double tp = bid - TakeProfitPoints * SymbolInfoDouble(Symbol(), SYMBOL_POINT);
    
    if(trade.Sell(LotSize, Symbol(), bid, sl, tp, 
                  StringFormat("CryptSIST SELL %.1f%%", currentConfidence * 100)))
    {
        lastTradeTime = TimeCurrent();
        dailyTradeCount++;
        totalTrades++;
        
        Print("✅ SELL ORDER EXECUTED");
        Print("💰 Price: ", bid);
        Print("🛡️ Stop Loss: ", sl);
        Print("🎯 Take Profit: ", tp);
        Print("📊 Confidence: ", DoubleToString(currentConfidence * 100, 1), "%");
    }
    else
    {
        Print("❌ SELL ORDER FAILED: ", trade.ResultRetcode(), " - ", trade.ResultRetcodeDescription());
    }
}

//+------------------------------------------------------------------+
//| Monitor active trades                                            |
//+------------------------------------------------------------------+
void MonitorActiveTrades()
{
    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
        if(position.SelectByIndex(i) && position.Symbol() == Symbol())
        {
            // Move to breakeven
            if(UseBreakEven)
                MoveToBreakEven();
            
            // Apply trailing stop
            if(UseTrailingStop)
                ApplyTrailingStop();
        }
    }
    
    // Update performance metrics
    UpdatePerformanceMetrics();
}

//+------------------------------------------------------------------+
//| Move stop loss to breakeven                                     |
//+------------------------------------------------------------------+
void MoveToBreakEven()
{
    double openPrice = position.PriceOpen();
    double currentSL = position.StopLoss();
    double point = SymbolInfoDouble(Symbol(), SYMBOL_POINT);
    
    if(position.PositionType() == POSITION_TYPE_BUY)
    {
        double bid = SymbolInfoDouble(Symbol(), SYMBOL_BID);
        if(bid >= openPrice + BreakEvenPoints * point && currentSL < openPrice)
        {
            trade.PositionModify(position.Ticket(), openPrice, position.TakeProfit());
            Print("🔄 Stop Loss moved to breakeven for BUY position");
        }
    }
    else if(position.PositionType() == POSITION_TYPE_SELL)
    {
        double ask = SymbolInfoDouble(Symbol(), SYMBOL_ASK);
        if(ask <= openPrice - BreakEvenPoints * point && currentSL > openPrice)
        {
            trade.PositionModify(position.Ticket(), openPrice, position.TakeProfit());
            Print("🔄 Stop Loss moved to breakeven for SELL position");
        }
    }
}

//+------------------------------------------------------------------+
//| Apply trailing stop                                             |
//+------------------------------------------------------------------+
void ApplyTrailingStop()
{
    double point = SymbolInfoDouble(Symbol(), SYMBOL_POINT);
    double trailDistance = TrailingStopPoints * point;
    
    if(position.PositionType() == POSITION_TYPE_BUY)
    {
        double bid = SymbolInfoDouble(Symbol(), SYMBOL_BID);
        double newSL = bid - trailDistance;
        
        if(newSL > position.StopLoss() && newSL > position.PriceOpen())
        {
            trade.PositionModify(position.Ticket(), newSL, position.TakeProfit());
            Print("🔄 Trailing stop updated for BUY position: ", newSL);
        }
    }
    else if(position.PositionType() == POSITION_TYPE_SELL)
    {
        double ask = SymbolInfoDouble(Symbol(), SYMBOL_ASK);
        double newSL = ask + trailDistance;
        
        if(newSL < position.StopLoss() && newSL < position.PriceOpen())
        {
            trade.PositionModify(position.Ticket(), newSL, position.TakeProfit());
            Print("🔄 Trailing stop updated for SELL position: ", newSL);
        }
    }
}

//+------------------------------------------------------------------+
//| Create live dashboard                                            |
//+------------------------------------------------------------------+
void CreateLiveDashboard()
{
    // Main dashboard background with better design
    string bgName = dashboardPrefix + "Background";
    if(ObjectCreate(0, bgName, OBJ_RECTANGLE_LABEL, 0, 0, 0))
    {
        ObjectSetInteger(0, bgName, OBJPROP_XDISTANCE, DashboardX);
        ObjectSetInteger(0, bgName, OBJPROP_YDISTANCE, DashboardY);
        ObjectSetInteger(0, bgName, OBJPROP_XSIZE, 320);
        ObjectSetInteger(0, bgName, OBJPROP_YSIZE, 160);
        ObjectSetInteger(0, bgName, OBJPROP_BGCOLOR, C'20,30,60'); // Dark blue
        ObjectSetInteger(0, bgName, OBJPROP_BORDER_TYPE, BORDER_RAISED);
        ObjectSetInteger(0, bgName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
        ObjectSetInteger(0, bgName, OBJPROP_COLOR, clrSteelBlue);
        ObjectSetInteger(0, bgName, OBJPROP_WIDTH, 2);
    }
    
    // Header background
    string headerName = dashboardPrefix + "Header";
    if(ObjectCreate(0, headerName, OBJ_RECTANGLE_LABEL, 0, 0, 0))
    {
        ObjectSetInteger(0, headerName, OBJPROP_XDISTANCE, DashboardX);
        ObjectSetInteger(0, headerName, OBJPROP_YDISTANCE, DashboardY);
        ObjectSetInteger(0, headerName, OBJPROP_XSIZE, 320);
        ObjectSetInteger(0, headerName, OBJPROP_YSIZE, 28);
        ObjectSetInteger(0, headerName, OBJPROP_BGCOLOR, C'0,120,215'); // Bright blue
        ObjectSetInteger(0, headerName, OBJPROP_BORDER_TYPE, BORDER_FLAT);
        ObjectSetInteger(0, headerName, OBJPROP_CORNER, CORNER_LEFT_UPPER);
    }
    
    // Dashboard title - simplified
    string titleName = dashboardPrefix + "Title";
    if(ObjectCreate(0, titleName, OBJ_LABEL, 0, 0, 0))
    {
        ObjectSetInteger(0, titleName, OBJPROP_XDISTANCE, DashboardX + 15);
        ObjectSetInteger(0, titleName, OBJPROP_YDISTANCE, DashboardY + 6);
        ObjectSetString(0, titleName, OBJPROP_TEXT, "🚀 CryptSIST");
        ObjectSetString(0, titleName, OBJPROP_FONT, "Arial Black");
        ObjectSetInteger(0, titleName, OBJPROP_FONTSIZE, 12);
        ObjectSetInteger(0, titleName, OBJPROP_COLOR, clrWhite);
    }
    
    // Status indicator
    string statusIndicator = dashboardPrefix + "StatusDot";
    if(ObjectCreate(0, statusIndicator, OBJ_LABEL, 0, 0, 0))
    {
        ObjectSetInteger(0, statusIndicator, OBJPROP_XDISTANCE, DashboardX + 280);
        ObjectSetInteger(0, statusIndicator, OBJPROP_YDISTANCE, DashboardY + 6);
        ObjectSetString(0, statusIndicator, OBJPROP_TEXT, "🟢 LIVE");
        ObjectSetInteger(0, statusIndicator, OBJPROP_FONTSIZE, 10);
        ObjectSetInteger(0, statusIndicator, OBJPROP_COLOR, clrLime);
        ObjectSetString(0, statusIndicator, OBJPROP_FONT, "Arial Bold");
    }
}

//+------------------------------------------------------------------+
//| Update live dashboard                                            |
//+------------------------------------------------------------------+
void UpdateLiveDashboard()
{
    // Signal status with enhanced display
    string signalName = dashboardPrefix + "Signal";
    if(ObjectFind(0, signalName) < 0)
        ObjectCreate(0, signalName, OBJ_LABEL, 0, 0, 0);
    
    ObjectSetInteger(0, signalName, OBJPROP_XDISTANCE, DashboardX + 15);
    ObjectSetInteger(0, signalName, OBJPROP_YDISTANCE, DashboardY + 40);
    
    color signalColor = clrWhite;
    string signalIcon = "⚪";
    
    if(currentSignal == SIGNAL_BUY) 
    {
        signalColor = clrLime;
        signalIcon = "🟢";
    }
    else if(currentSignal == SIGNAL_SELL) 
    {
        signalColor = clrRed; 
        signalIcon = "🔴";
    }
    else if(currentSignal == SIGNAL_HOLD) 
    {
        signalColor = clrYellow;
        signalIcon = "🟡";
    }
    
    string signalText = StringFormat("%s SIGNAL: %s (%.0f%%)", 
                                     signalIcon,
                                     EnumToString(currentSignal), 
                                     currentConfidence * 100);
    
    ObjectSetString(0, signalName, OBJPROP_TEXT, signalText);
    ObjectSetInteger(0, signalName, OBJPROP_COLOR, signalColor);
    ObjectSetInteger(0, signalName, OBJPROP_FONTSIZE, 12);
    ObjectSetString(0, signalName, OBJPROP_FONT, "Arial Black");
    
    // Market sentiment with emoji
    string sentimentName = dashboardPrefix + "Sentiment";
    if(ObjectFind(0, sentimentName) < 0)
        ObjectCreate(0, sentimentName, OBJ_LABEL, 0, 0, 0);
    
    ObjectSetInteger(0, sentimentName, OBJPROP_XDISTANCE, DashboardX + 15);
    ObjectSetInteger(0, sentimentName, OBJPROP_YDISTANCE, DashboardY + 65);
    
    string sentimentEmoji = "😐";
    if(marketSentiment == "BULLISH") sentimentEmoji = "😊";
    else if(marketSentiment == "BEARISH") sentimentEmoji = "😟";
    else if(marketSentiment == "VERY_BULLISH") sentimentEmoji = "🤑";
    else if(marketSentiment == "VERY_BEARISH") sentimentEmoji = "😰";
    
    ObjectSetString(0, sentimentName, OBJPROP_TEXT, sentimentEmoji + " Sentiment: " + marketSentiment);
    ObjectSetInteger(0, sentimentName, OBJPROP_COLOR, clrWhite);
    ObjectSetInteger(0, sentimentName, OBJPROP_FONTSIZE, 10);
    
    // Trading statistics
    string statusName = dashboardPrefix + "Status";
    if(ObjectFind(0, statusName) < 0)
        ObjectCreate(0, statusName, OBJ_LABEL, 0, 0, 0);
    
    ObjectSetInteger(0, statusName, OBJPROP_XDISTANCE, DashboardX + 15);
    ObjectSetInteger(0, statusName, OBJPROP_YDISTANCE, DashboardY + 85);
    
    string statusText = StringFormat("� Trades: %d/%d | Active: %d | Pending: %d", 
                                     dailyTradeCount, MaxDailyTrades, 
                                     PositionsTotal(), OrdersTotal());
    
    ObjectSetString(0, statusName, OBJPROP_TEXT, statusText);
    ObjectSetInteger(0, statusName, OBJPROP_COLOR, clrWhite);
    ObjectSetInteger(0, statusName, OBJPROP_FONTSIZE, 9);
    
    // Performance with color coding
    string perfName = dashboardPrefix + "Performance";
    if(ObjectFind(0, perfName) < 0)
        ObjectCreate(0, perfName, OBJ_LABEL, 0, 0, 0);
    
    ObjectSetInteger(0, perfName, OBJPROP_XDISTANCE, DashboardX + 15);
    ObjectSetInteger(0, perfName, OBJPROP_YDISTANCE, DashboardY + 105);
    
    double winRate = totalTrades > 0 ? (double)winningTrades / totalTrades * 100 : 0;
    string perfIcon = totalProfit >= 0 ? "📈" : "📉";
    string perfText = StringFormat("%s Win Rate: %.1f%% | Profit: $%.2f", 
                                   perfIcon, winRate, totalProfit);
    
    ObjectSetString(0, perfName, OBJPROP_TEXT, perfText);
    ObjectSetInteger(0, perfName, OBJPROP_COLOR, totalProfit >= 0 ? clrLime : clrRed);
    ObjectSetInteger(0, perfName, OBJPROP_FONTSIZE, 10);
    ObjectSetString(0, perfName, OBJPROP_FONT, "Arial Bold");
    
    // Current price with trend indicator
    string priceName = dashboardPrefix + "Price";
    if(ObjectFind(0, priceName) < 0)
        ObjectCreate(0, priceName, OBJ_LABEL, 0, 0, 0);
    
    ObjectSetInteger(0, priceName, OBJPROP_XDISTANCE, DashboardX + 15);
    ObjectSetInteger(0, priceName, OBJPROP_YDISTANCE, DashboardY + 118);
    
    string trendIcon = "➡️";
    static double lastPrice = 0;
    if(currentPrice > lastPrice) trendIcon = "⬆️";
    else if(currentPrice < lastPrice) trendIcon = "⬇️";
    lastPrice = currentPrice;
    
    string priceText = StringFormat("%s %s: %.5f", trendIcon, Symbol(), currentPrice);
    ObjectSetString(0, priceName, OBJPROP_TEXT, priceText);
    ObjectSetInteger(0, priceName, OBJPROP_COLOR, clrWhite);
    ObjectSetInteger(0, priceName, OBJPROP_FONTSIZE, 10);
    
    // Last update time (WIB = UTC+7)
    string timeName = dashboardPrefix + "Time";
    if(ObjectFind(0, timeName) < 0)
        ObjectCreate(0, timeName, OBJ_LABEL, 0, 0, 0);
    
    ObjectSetInteger(0, timeName, OBJPROP_XDISTANCE, DashboardX + 15);
    ObjectSetInteger(0, timeName, OBJPROP_YDISTANCE, DashboardY + 138);
    
    // Convert to WIB (UTC+7)
    datetime wibTime = TimeCurrent() + 7 * 3600; // Add 7 hours for WIB
    string timeText = "🕐 WIB: " + TimeToString(wibTime, TIME_MINUTES);
    ObjectSetString(0, timeName, OBJPROP_TEXT, timeText);
    ObjectSetInteger(0, timeName, OBJPROP_COLOR, clrSilver);
    ObjectSetInteger(0, timeName, OBJPROP_FONTSIZE, 9);
}

//+------------------------------------------------------------------+
//| Show signal arrow on chart                                      |
//+------------------------------------------------------------------+
void ShowSignalArrow()
{
    string arrowName = signalPrefix + IntegerToString(TimeCurrent());
    
    int arrowCode = 0;
    color arrowColor = clrWhite;
    
    if(currentSignal == SIGNAL_BUY)
    {
        arrowCode = 233; // Up arrow
        arrowColor = BuySignalColor;
    }
    else if(currentSignal == SIGNAL_SELL)
    {
        arrowCode = 234; // Down arrow  
        arrowColor = SellSignalColor;
    }
    else if(currentSignal == SIGNAL_HOLD)
    {
        arrowCode = 108; // Circle
        arrowColor = HoldSignalColor;
    }
    else
        return;
    
    if(ObjectCreate(0, arrowName, OBJ_ARROW, 0, TimeCurrent(), currentPrice))
    {
        ObjectSetInteger(0, arrowName, OBJPROP_ARROWCODE, arrowCode);
        ObjectSetInteger(0, arrowName, OBJPROP_COLOR, arrowColor);
        ObjectSetInteger(0, arrowName, OBJPROP_WIDTH, SignalArrowSize);
        ObjectSetString(0, arrowName, OBJPROP_TEXT, 
                        StringFormat("%s - %.1f%%", EnumToString(currentSignal), currentConfidence * 100));
    }
}

//+------------------------------------------------------------------+
//| Play sound alert                                                |
//+------------------------------------------------------------------+
void PlaySignalSound()
{
    if(currentSignal == SIGNAL_BUY)
        PlaySound("alert.wav");
    else if(currentSignal == SIGNAL_SELL)
        PlaySound("alert2.wav");
    else if(currentSignal == SIGNAL_HOLD)
        PlaySound("timeout.wav");
}

//+------------------------------------------------------------------+
//| Send push notification                                           |
//+------------------------------------------------------------------+
void SendPushNotification()
{
    string message = StringFormat("🚀 CryptSIST %s: %s Signal (%.1f%% confidence) on %s", 
                                  Symbol(), EnumToString(currentSignal), 
                                  currentConfidence * 100, Symbol());
    SendNotification(message);
}

//+------------------------------------------------------------------+
//| Log signal to file                                              |
//+------------------------------------------------------------------+
void LogSignalToFile()
{
    string filename = "CryptSIST_Signals_" + Symbol() + ".csv";
    int file = FileOpen(filename, FILE_WRITE | FILE_CSV | FILE_COMMON);
    
    if(file != INVALID_HANDLE)
    {
        if(FileSize(file) == 0)
        {
            // Write header
            FileWrite(file, "Timestamp", "Symbol", "Signal", "Confidence", "Price", "Sentiment", "Analysis");
        }
        
        FileSeek(file, 0, SEEK_END);
        FileWrite(file, TimeToString(TimeCurrent()), Symbol(), EnumToString(currentSignal), 
                  currentConfidence, currentPrice, marketSentiment, currentAnalysis);
        FileClose(file);
    }
}

//+------------------------------------------------------------------+
//| Update performance metrics                                       |
//+------------------------------------------------------------------+
void UpdatePerformanceMetrics()
{
    double currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    totalProfit = currentBalance - initialBalance;
    
    // Calculate drawdown
    static double peakBalance = 0;
    if(currentBalance > peakBalance)
        peakBalance = currentBalance;
    
    currentDrawdown = (peakBalance - currentBalance) / peakBalance * 100;
    if(currentDrawdown > maxDrawdown)
        maxDrawdown = currentDrawdown;
    
    // Count winning trades
    winningTrades = 0;
    for(int i = 0; i < HistoryDealsTotal(); i++)
    {
        if(HistoryDealSelect(i))
        {
            if(HistoryDealGetInteger(i, DEAL_MAGIC) == 123456 && 
               HistoryDealGetDouble(i, DEAL_PROFIT) > 0)
                winningTrades++;
        }
    }
}

//+------------------------------------------------------------------+
//| Check for new trading day                                       |
//+------------------------------------------------------------------+
void CheckNewDay()
{
    datetime currentDate = TimeTradeServer();
    MqlDateTime current_time, last_time;
    TimeToStruct(currentDate, current_time);
    TimeToStruct(lastTradeDate, last_time);
    
    if(current_time.day != last_time.day || current_time.mon != last_time.mon || current_time.year != last_time.year)
    {
        dailyTradeCount = 0;
        lastTradeDate = currentDate;
        Print("📅 New trading day started - Trade counter reset");
    }
}

//+------------------------------------------------------------------+
//| Test server connection                                           |
//+------------------------------------------------------------------+
void TestServerConnection()
{
    string url = ServerURL + "/health";
    string response = HttpRequest(url);
    
    if(StringLen(response) > 0)
    {
        Print("✅ CryptSIST server connection successful!");
        Print("📡 Server URL: ", ServerURL);
    }
    else
    {
        Print("⚠️ Cannot connect to CryptSIST server");
        Print("🔧 Please check server URL: ", ServerURL);
    }
}

//+------------------------------------------------------------------+
//| Clean up all chart objects                                      |
//+------------------------------------------------------------------+
void CleanupAllObjects()
{
    for(int i = ObjectsTotal(0) - 1; i >= 0; i--)
    {
        string objName = ObjectName(0, i);
        if(StringFind(objName, dashboardPrefix) >= 0 || 
           StringFind(objName, signalPrefix) >= 0 || 
           StringFind(objName, analysisPrefix) >= 0)
        {
            ObjectDelete(0, objName);
        }
    }
}

//+------------------------------------------------------------------+
//| HTTP Request function                                            |
//+------------------------------------------------------------------+
string HttpRequest(string url, string method = "GET", string data = "")
{
    char post[], result[];
    string headers;
    
    if(StringLen(data) > 0)
    {
        StringToCharArray(data, post, 0, StringLen(data));
        headers = "Content-Type: application/json\r\n";
    }
    
    int timeout = RequestTimeout;
    int res = WebRequest(method, url, headers, timeout, post, result, headers);
    
    if(res == 200)
    {
        return CharArrayToString(result);
    }
    else
    {
        if(res == -1)
        {
            Print("⚠️ WebRequest error. Please add URL to allowed list:");
            Print("Tools -> Options -> Expert Advisors -> Allow WebRequest for: ", url);
        }
        else
        {
            Print("⚠️ HTTP Error: ", res);
        }
        return "";
    }
}

//+------------------------------------------------------------------+
//| Helper functions for technical analysis                         |
//+------------------------------------------------------------------+
double CalculateMA(const MqlRates &rates[], int period)
{
    if(ArraySize(rates) < period) return 0;
    
    double sum = 0;
    for(int i = 0; i < period; i++)
    {
        sum += rates[ArraySize(rates) - 1 - i].close;
    }
    return sum / period;
}

double CalculateRSI(const MqlRates &rates[], int period)
{
    if(ArraySize(rates) < period + 1) return 50;
    
    double gains = 0, losses = 0;
    
    for(int i = 1; i <= period; i++)
    {
        double change = rates[ArraySize(rates) - i].close - rates[ArraySize(rates) - i - 1].close;
        if(change > 0) gains += change;
        else losses -= change;
    }
    
    double avgGain = gains / period;
    double avgLoss = losses / period;
    
    if(avgLoss == 0) return 100;
    
    double rs = avgGain / avgLoss;
    return 100 - (100 / (1 + rs));
}

void CalculateMACD(const MqlRates &rates[], double &macd[], double &signal[], double &histogram[])
{
    int size = ArraySize(rates);
    if(size < 35) return;
    
    ArrayResize(macd, 2);
    ArrayResize(signal, 2);
    ArrayResize(histogram, 2);
    
    // Calculate current MACD
    double ema12_0 = CalculateEMA(rates, 12);
    double ema26_0 = CalculateEMA(rates, 26);
    
    macd[0] = ema12_0 - ema26_0;
    signal[0] = macd[0] * 0.8; // Simplified signal line
    histogram[0] = macd[0] - signal[0];
    
    // Calculate previous MACD (simplified)
    if(size >= 36)
    {
        MqlRates prevRates[];
        ArrayCopy(prevRates, rates, 0, 0, size - 1);
        double ema12_1 = CalculateEMA(prevRates, 12);
        double ema26_1 = CalculateEMA(prevRates, 26);
        
        macd[1] = ema12_1 - ema26_1;
        signal[1] = macd[1] * 0.8;
        histogram[1] = macd[1] - signal[1];
    }
    else
    {
        // If not enough data, use current values
        macd[1] = macd[0];
        signal[1] = signal[0];
        histogram[1] = histogram[0];
    }
}

double CalculateEMA(const MqlRates &rates[], int period)
{
    if(ArraySize(rates) < period) return 0;
    
    double multiplier = 2.0 / (period + 1);
    double ema = rates[ArraySize(rates) - period].close;
    
    for(int i = ArraySize(rates) - period + 1; i < ArraySize(rates); i++)
    {
        ema = rates[i].close * multiplier + ema * (1 - multiplier);
    }
    
    return ema;
}

double CalculateATR(int period)
{
    MqlRates rates[];
    if(CopyRates(Symbol(), PERIOD_CURRENT, 0, period + 1, rates) <= period)
        return 0;
    
    double atr = 0;
    for(int i = 1; i <= period; i++)
    {
        double tr = MathMax(rates[i].high - rates[i].low,
                           MathMax(MathAbs(rates[i].high - rates[i-1].close),
                                  MathAbs(rates[i].low - rates[i-1].close)));
        atr += tr;
    }
    
    return atr / period;
}
