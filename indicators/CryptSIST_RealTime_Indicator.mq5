//+------------------------------------------------------------------+
//|                                    CryptSIST_RealTime_Indicator.mq5 |
//|                                    CryptSIST Development Team     |
//|                                             https://cryptsist.com |
//+------------------------------------------------------------------+
#property copyright "CryptSIST Development Team"
#property link      "https://cryptsist.com"
#property version   "3.00"
#property indicator_chart_window

#property indicator_buffers 8
#property indicator_plots   6

//--- Plot Buy signals
#property indicator_label1  "🟢 CryptSIST BUY"
#property indicator_type1   DRAW_ARROW
#property indicator_color1  clrLime
#property indicator_style1  STYLE_SOLID
#property indicator_width1  4

//--- Plot Sell signals  
#property indicator_label2  "🔴 CryptSIST SELL"
#property indicator_type2   DRAW_ARROW
#property indicator_color2  clrRed
#property indicator_style2  STYLE_SOLID
#property indicator_width2  4

//--- Plot Hold signals
#property indicator_label3  "🟡 CryptSIST HOLD"
#property indicator_type3   DRAW_ARROW
#property indicator_color3  clrYellow
#property indicator_style3  STYLE_SOLID
#property indicator_width3  3

//--- Plot Confidence High
#property indicator_label4  "⭐ High Confidence"
#property indicator_type4   DRAW_ARROW
#property indicator_color4  clrGold
#property indicator_style4  STYLE_SOLID
#property indicator_width4  2

//--- Plot Trend line
#property indicator_label5  "📈 Trend Direction"
#property indicator_type5   DRAW_LINE
#property indicator_color5  clrBlue
#property indicator_style5  STYLE_SOLID
#property indicator_width5  2

//--- Plot Sentiment line
#property indicator_label6  "🎭 Market Sentiment"
#property indicator_type6   DRAW_LINE
#property indicator_color6  clrOrange
#property indicator_style6  STYLE_DOT
#property indicator_width6  1

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

//--- Input parameters
input group "=== 🚀 Real-Time Analysis ==="
input string ServerURL = "http://127.0.0.1:8000";        // CryptSIST Server URL
input int UpdateIntervalMS = 1000;                       // Update interval (milliseconds)
input double HighConfidenceThreshold = 0.8;              // High confidence threshold
input bool ShowLiveAnalysis = true;                      // Show live analysis on chart
input bool ShowConfidenceLevel = true;                   // Show confidence percentage
input bool EnableRealTimeUpdates = true;                 // Enable real-time updates
input bool ShowTrendAnalysis = true;                     // Show trend analysis

input group "=== 📊 Visual Settings ==="
input color BuyArrowColor = clrLime;                     // Buy arrow color
input color SellArrowColor = clrRed;                     // Sell arrow color
input color HoldArrowColor = clrYellow;                  // Hold arrow color
input color HighConfidenceColor = clrGold;               // High confidence color
input color TrendLineColor = clrBlue;                    // Trend line color
input color SentimentLineColor = clrOrange;              // Sentiment line color
input int ArrowSize = 4;                                 // Arrow size

input group "=== 🎯 Analysis Display ==="
input bool ShowAnalysisText = true;                     // Show analysis text
input bool ShowConfidenceBar = true;                    // Show confidence bar
input bool ShowMarketSentiment = true;                  // Show market sentiment
input int MaxTextObjects = 50;                          // Maximum text objects on chart
input bool AutoCleanOldObjects = true;                  // Auto clean old objects

//--- Indicator buffers
double BuyBuffer[];
double SellBuffer[];
double HoldBuffer[];
double HighConfidenceBuffer[];
double TrendBuffer[];
double SentimentBuffer[];
double ConfidenceBuffer[];
double SignalStrengthBuffer[];

//--- Global variables
datetime lastUpdateTime = 0;
datetime lastSignalTime = 0;
int textObjectCounter = 0;
string currentSymbol;

// Analysis data
ENUM_SIGNAL_TYPE currentSignal = SIGNAL_NONE;
ENUM_SIGNAL_TYPE lastSignal = SIGNAL_NONE;
double currentConfidence = 0.0;
double lastConfidence = 0.0;
string currentAnalysis = "";
string marketSentiment = "NEUTRAL";
double sentimentScore = 0.0;
double trendDirection = 0.0;

// Visual objects
string analysisTextPrefix = "CryptSIST_Analysis_";
string confidenceTextPrefix = "CryptSIST_Confidence_";
string sentimentTextPrefix = "CryptSIST_Sentiment_";

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("🚀 CryptSIST Real-Time Indicator v3.0 Starting...");
    
    // Set buffers as indicator buffers
    SetIndexBuffer(0, BuyBuffer, INDICATOR_DATA);
    SetIndexBuffer(1, SellBuffer, INDICATOR_DATA);
    SetIndexBuffer(2, HoldBuffer, INDICATOR_DATA);
    SetIndexBuffer(3, HighConfidenceBuffer, INDICATOR_DATA);
    SetIndexBuffer(4, TrendBuffer, INDICATOR_DATA);
    SetIndexBuffer(5, SentimentBuffer, INDICATOR_DATA);
    SetIndexBuffer(6, ConfidenceBuffer, INDICATOR_CALCULATIONS);
    SetIndexBuffer(7, SignalStrengthBuffer, INDICATOR_CALCULATIONS);
    
    // Set arrow codes
    PlotIndexSetInteger(0, PLOT_ARROW, 233);  // Up arrow for BUY
    PlotIndexSetInteger(1, PLOT_ARROW, 234);  // Down arrow for SELL
    PlotIndexSetInteger(2, PLOT_ARROW, 108);  // Circle for HOLD
    PlotIndexSetInteger(3, PLOT_ARROW, 159);  // Star for high confidence
    
    // Set colors
    PlotIndexSetInteger(0, PLOT_LINE_COLOR, BuyArrowColor);
    PlotIndexSetInteger(1, PLOT_LINE_COLOR, SellArrowColor);
    PlotIndexSetInteger(2, PLOT_LINE_COLOR, HoldArrowColor);
    PlotIndexSetInteger(3, PLOT_LINE_COLOR, HighConfidenceColor);
    PlotIndexSetInteger(4, PLOT_LINE_COLOR, TrendLineColor);
    PlotIndexSetInteger(5, PLOT_LINE_COLOR, SentimentLineColor);
    
    // Set line widths
    PlotIndexSetInteger(0, PLOT_LINE_WIDTH, ArrowSize);
    PlotIndexSetInteger(1, PLOT_LINE_WIDTH, ArrowSize);
    PlotIndexSetInteger(2, PLOT_LINE_WIDTH, ArrowSize - 1);
    PlotIndexSetInteger(3, PLOT_LINE_WIDTH, ArrowSize - 2);
    PlotIndexSetInteger(4, PLOT_LINE_WIDTH, 2);
    PlotIndexSetInteger(5, PLOT_LINE_WIDTH, 1);
    
    // Initialize arrays
    ArraySetAsSeries(BuyBuffer, true);
    ArraySetAsSeries(SellBuffer, true);
    ArraySetAsSeries(HoldBuffer, true);
    ArraySetAsSeries(HighConfidenceBuffer, true);
    ArraySetAsSeries(TrendBuffer, true);
    ArraySetAsSeries(SentimentBuffer, true);
    ArraySetAsSeries(ConfidenceBuffer, true);
    ArraySetAsSeries(SignalStrengthBuffer, true);
    
    // Set empty values
    PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, 0.0);
    PlotIndexSetDouble(1, PLOT_EMPTY_VALUE, 0.0);
    PlotIndexSetDouble(2, PLOT_EMPTY_VALUE, 0.0);
    PlotIndexSetDouble(3, PLOT_EMPTY_VALUE, 0.0);
    PlotIndexSetDouble(4, PLOT_EMPTY_VALUE, 0.0);
    PlotIndexSetDouble(5, PLOT_EMPTY_VALUE, 0.0);
    
    // Get current symbol
    currentSymbol = Symbol();
    
    // Test server connection
    TestServerConnection();
    
    Print("✅ CryptSIST Real-Time Indicator initialized successfully!");
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Custom indicator deinitialization function                       |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    // Clean up text objects
    if(AutoCleanOldObjects)
        CleanupAllTextObjects();
    
    Print("👋 CryptSIST Real-Time Indicator stopped!");
}

//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{
    if(rates_total < 10) return(0);
    
    // Set arrays as series
    ArraySetAsSeries(time, true);
    ArraySetAsSeries(close, true);
    ArraySetAsSeries(high, true);
    ArraySetAsSeries(low, true);
    
    // Real-time update check
    if(EnableRealTimeUpdates)
    {
        if(GetTickCount() - lastUpdateTime > UpdateIntervalMS)
        {
            PerformRealTimeAnalysis();
            lastUpdateTime = GetTickCount();
        }
    }
    
    // Calculate for recent bars
    int start = MathMax(0, prev_calculated - 1);
    
    for(int i = start; i < rates_total && i < 1000; i++) // Limit to 1000 bars for performance
    {
        int reverseIndex = rates_total - 1 - i;
        
        // Clear previous values
        BuyBuffer[reverseIndex] = 0.0;
        SellBuffer[reverseIndex] = 0.0;
        HoldBuffer[reverseIndex] = 0.0;
        HighConfidenceBuffer[reverseIndex] = 0.0;
        TrendBuffer[reverseIndex] = 0.0;
        SentimentBuffer[reverseIndex] = 0.0;
        
        // For current bar (real-time analysis)
        if(reverseIndex == 0)
        {
            ApplyCurrentSignalToBuffers(close[reverseIndex]);
        }
        else if(reverseIndex < 100) // Apply historical analysis for recent bars
        {
            ApplyHistoricalAnalysis(reverseIndex, time[reverseIndex], close[reverseIndex], 
                                   high[reverseIndex], low[reverseIndex]);
        }
    }
    
    return(rates_total);
}

//+------------------------------------------------------------------+
//| Perform real-time analysis                                       |
//+------------------------------------------------------------------+
void PerformRealTimeAnalysis()
{
    // Store previous values
    lastSignal = currentSignal;
    lastConfidence = currentConfidence;
    
    // Get CryptSIST analysis
    GetCryptSISTRealTimeAnalysis();
    
    // Perform additional technical analysis
    PerformSupplementaryAnalysis();
    
    // Check for significant changes
    if(currentSignal != lastSignal || MathAbs(currentConfidence - lastConfidence) > 0.1)
    {
        ProcessSignalChange();
    }
    
    // Update visual elements
    if(ShowLiveAnalysis)
        UpdateLiveAnalysisDisplay();
}

//+------------------------------------------------------------------+
//| Get real-time analysis from CryptSIST server                     |
//+------------------------------------------------------------------+
void GetCryptSISTRealTimeAnalysis()
{
    string url = ServerURL + "/signal/" + currentSymbol;
    string response = HttpRequest(url);
    
    if(StringLen(response) > 0)
    {
        ParseRealTimeResponse(response);
        Print("📡 Live data received from CryptSIST server");
    }
    else
    {
        // Fallback to technical analysis
        PerformFallbackAnalysis();
        Print("🔧 Using fallback technical analysis");
    }
}

//+------------------------------------------------------------------+
//| Parse real-time response from server                             |
//+------------------------------------------------------------------+
void ParseRealTimeResponse(string response)
{
    // Enhanced JSON parsing for real-time data
    if(StringFind(response, "\"signal\":\"BUY\"") >= 0)
    {
        currentSignal = SIGNAL_BUY;
        currentAnalysis = "🟢 CryptSIST: STRONG BUY SIGNAL";
    }
    else if(StringFind(response, "\"signal\":\"SELL\"") >= 0)
    {
        currentSignal = SIGNAL_SELL;
        currentAnalysis = "🔴 CryptSIST: STRONG SELL SIGNAL";
    }
    else if(StringFind(response, "\"signal\":\"HOLD\"") >= 0)
    {
        currentSignal = SIGNAL_HOLD;
        currentAnalysis = "🟡 CryptSIST: HOLD POSITION";
    }
    else
    {
        currentSignal = SIGNAL_NONE;
        currentAnalysis = "⚪ CryptSIST: NO CLEAR SIGNAL";
    }
    
    // Extract confidence with error handling
    int confStart = StringFind(response, "\"confidence\":");
    if(confStart >= 0)
    {
        int confEnd = StringFind(response, ",", confStart);
        if(confEnd == -1) confEnd = StringFind(response, "}", confStart);
        
        if(confEnd > confStart)
        {
            string confStr = StringSubstr(response, confStart + 13, confEnd - confStart - 13);
            StringReplace(confStr, "\"", "");
            StringReplace(confStr, " ", "");
            currentConfidence = StringToDouble(confStr);
        }
    }
    
    // Extract market sentiment
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
    else if(StringFind(response, "\"sentiment\":\"NEUTRAL\"") >= 0)
    {
        marketSentiment = "NEUTRAL";
        sentimentScore = 0.0;
    }
    
    // Extract trend direction
    if(StringFind(response, "\"trend\":\"UP\"") >= 0)
        trendDirection = 1.0;
    else if(StringFind(response, "\"trend\":\"DOWN\"") >= 0)
        trendDirection = -1.0;
    else
        trendDirection = 0.0;
    
    // Extract additional analysis info
    int analysisStart = StringFind(response, "\"analysis\":\"");
    if(analysisStart >= 0)
    {
        int analysisEnd = StringFind(response, "\"", analysisStart + 12);
        if(analysisEnd > analysisStart)
        {
            string extractedAnalysis = StringSubstr(response, analysisStart + 12, analysisEnd - analysisStart - 12);
            if(StringLen(extractedAnalysis) > 0)
                currentAnalysis = extractedAnalysis;
        }
    }
}

//+------------------------------------------------------------------+
//| Perform supplementary technical analysis                         |
//+------------------------------------------------------------------+
void PerformSupplementaryAnalysis()
{
    MqlRates rates[];
    if(CopyRates(currentSymbol, PERIOD_CURRENT, 0, 50, rates) < 50)
        return;
    
    // Calculate additional indicators
    double ma20 = CalculateMA(rates, 20);
    double ma50 = CalculateMA(rates, 50);
    double rsi = CalculateRSI(rates, 14);
    double atr = CalculateATR(rates, 14);
    
    double currentPrice = SymbolInfoDouble(currentSymbol, SYMBOL_BID);
    
    // Adjust confidence based on technical indicators
    double techConfidence = currentConfidence;
    
    // RSI confirmation
    if(currentSignal == SIGNAL_BUY && rsi < 70)
        techConfidence += 0.05;
    else if(currentSignal == SIGNAL_SELL && rsi > 30)
        techConfidence += 0.05;
    
    // Moving average confirmation
    if(currentSignal == SIGNAL_BUY && currentPrice > ma20 && ma20 > ma50)
        techConfidence += 0.1;
    else if(currentSignal == SIGNAL_SELL && currentPrice < ma20 && ma20 < ma50)
        techConfidence += 0.1;
    
    // Volatility adjustment
    if(atr > SymbolInfoDouble(currentSymbol, SYMBOL_POINT) * 500)
        techConfidence -= 0.1; // Reduce confidence in high volatility
    
    currentConfidence = MathMax(0.0, MathMin(1.0, techConfidence));
}

//+------------------------------------------------------------------+
//| Perform fallback analysis when server is unavailable            |
//+------------------------------------------------------------------+
void PerformFallbackAnalysis()
{
    MqlRates rates[];
    if(CopyRates(currentSymbol, PERIOD_CURRENT, 0, 50, rates) < 50)
        return;
    
    double ma20 = CalculateMA(rates, 20);
    double ma50 = CalculateMA(rates, 50);
    double rsi = CalculateRSI(rates, 14);
    double currentPrice = SymbolInfoDouble(currentSymbol, SYMBOL_BID);
    
    // Simple technical analysis
    if(currentPrice > ma20 && ma20 > ma50 && rsi > 40 && rsi < 70)
    {
        currentSignal = SIGNAL_BUY;
        currentConfidence = 0.6;
        currentAnalysis = "🔧 Technical: BUY (MA Crossover)";
        marketSentiment = "BULLISH";
        trendDirection = 1.0;
    }
    else if(currentPrice < ma20 && ma20 < ma50 && rsi > 30 && rsi < 60)
    {
        currentSignal = SIGNAL_SELL;
        currentConfidence = 0.6;
        currentAnalysis = "🔧 Technical: SELL (MA Crossover)";
        marketSentiment = "BEARISH";
        trendDirection = -1.0;
    }
    else
    {
        currentSignal = SIGNAL_HOLD;
        currentConfidence = 0.5;
        currentAnalysis = "🔧 Technical: HOLD (Sideways)";
        marketSentiment = "NEUTRAL";
        trendDirection = 0.0;
    }
}

//+------------------------------------------------------------------+
//| Apply current signal to indicator buffers                        |
//+------------------------------------------------------------------+
void ApplyCurrentSignalToBuffers(double price)
{
    int currentIndex = 0;
    
    // Apply signal to appropriate buffer
    if(currentSignal == SIGNAL_BUY)
    {
        BuyBuffer[currentIndex] = price;
        if(currentConfidence >= HighConfidenceThreshold)
            HighConfidenceBuffer[currentIndex] = price;
    }
    else if(currentSignal == SIGNAL_SELL)
    {
        SellBuffer[currentIndex] = price;
        if(currentConfidence >= HighConfidenceThreshold)
            HighConfidenceBuffer[currentIndex] = price;
    }
    else if(currentSignal == SIGNAL_HOLD)
    {
        HoldBuffer[currentIndex] = price;
    }
    
    // Apply trend and sentiment
    if(ShowTrendAnalysis)
    {
        TrendBuffer[currentIndex] = price + (trendDirection * 100 * SymbolInfoDouble(currentSymbol, SYMBOL_POINT));
        SentimentBuffer[currentIndex] = price + (sentimentScore * 50 * SymbolInfoDouble(currentSymbol, SYMBOL_POINT));
    }
    
    // Store confidence for calculations
    ConfidenceBuffer[currentIndex] = currentConfidence;
    SignalStrengthBuffer[currentIndex] = (double)currentSignal;
}

//+------------------------------------------------------------------+
//| Apply historical analysis for past bars                          |
//+------------------------------------------------------------------+
void ApplyHistoricalAnalysis(int index, datetime barTime, double price, double high, double low)
{
    // This is a simplified historical analysis
    // In a real implementation, you would have stored historical signals
    
    // For demonstration, apply some pattern-based signals
    static int lastHistoricalSignal = SIGNAL_NONE;
    
    // Simple pattern recognition
    if(index % 10 == 0) // Every 10th bar, simulate a signal
    {
        if(price > high * 0.98) // Near high
        {
            if(lastHistoricalSignal != SIGNAL_BUY)
            {
                BuyBuffer[index] = price;
                lastHistoricalSignal = SIGNAL_BUY;
            }
        }
        else if(price < low * 1.02) // Near low
        {
            if(lastHistoricalSignal != SIGNAL_SELL)
            {
                SellBuffer[index] = price;
                lastHistoricalSignal = SIGNAL_SELL;
            }
        }
        else
        {
            if(lastHistoricalSignal != SIGNAL_HOLD)
            {
                HoldBuffer[index] = price;
                lastHistoricalSignal = SIGNAL_HOLD;
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Process signal change                                            |
//+------------------------------------------------------------------+
void ProcessSignalChange()
{
    // Update signal time
    lastSignalTime = TimeCurrent();
    
    // Display analysis text
    if(ShowAnalysisText)
        DisplayAnalysisText();
    
    // Display confidence information
    if(ShowConfidenceLevel)
        DisplayConfidenceInfo();
    
    // Display market sentiment
    if(ShowMarketSentiment)
        DisplaySentimentInfo();
    
    // Clean up old objects if needed
    if(AutoCleanOldObjects && textObjectCounter > MaxTextObjects)
        CleanupOldTextObjects();
    
    // Log the signal change
    string logMessage = StringFormat("📊 Signal Change: %s -> %s (Confidence: %.1f%% -> %.1f%%)",
                                     EnumToString(lastSignal), EnumToString(currentSignal),
                                     lastConfidence * 100, currentConfidence * 100);
    Print(logMessage);
}

//+------------------------------------------------------------------+
//| Display analysis text on chart                                   |
//+------------------------------------------------------------------+
void DisplayAnalysisText()
{
    if(currentSignal == SIGNAL_NONE) return;
    
    string textName = analysisTextPrefix + IntegerToString(textObjectCounter);
    double price = SymbolInfoDouble(currentSymbol, SYMBOL_BID);
    
    if(ObjectCreate(0, textName, OBJ_TEXT, 0, TimeCurrent(), price))
    {
        ObjectSetString(0, textName, OBJPROP_TEXT, currentAnalysis);
        ObjectSetString(0, textName, OBJPROP_FONT, "Arial");
        ObjectSetInteger(0, textName, OBJPROP_FONTSIZE, 9);
        
        color textColor = clrWhite;
        if(currentSignal == SIGNAL_BUY) textColor = BuyArrowColor;
        else if(currentSignal == SIGNAL_SELL) textColor = SellArrowColor;
        else if(currentSignal == SIGNAL_HOLD) textColor = HoldArrowColor;
        
        ObjectSetInteger(0, textName, OBJPROP_COLOR, textColor);
        ObjectSetInteger(0, textName, OBJPROP_ANCHOR, ANCHOR_LEFT);
        
        textObjectCounter++;
    }
}

//+------------------------------------------------------------------+
//| Display confidence information                                   |
//+------------------------------------------------------------------+
void DisplayConfidenceInfo()
{
    string confName = confidenceTextPrefix + IntegerToString(textObjectCounter);
    double price = SymbolInfoDouble(currentSymbol, SYMBOL_BID);
    double offset = 50 * SymbolInfoDouble(currentSymbol, SYMBOL_POINT);
    
    if(ObjectCreate(0, confName, OBJ_TEXT, 0, TimeCurrent(), price + offset))
    {
        string confText = StringFormat("🎯 %.1f%%", currentConfidence * 100);
        ObjectSetString(0, confName, OBJPROP_TEXT, confText);
        ObjectSetString(0, confName, OBJPROP_FONT, "Arial Bold");
        ObjectSetInteger(0, confName, OBJPROP_FONTSIZE, 8);
        
        color confColor = clrGray;
        if(currentConfidence >= 0.8) confColor = clrGold;
        else if(currentConfidence >= 0.6) confColor = clrYellow;
        else if(currentConfidence >= 0.4) confColor = clrOrange;
        
        ObjectSetInteger(0, confName, OBJPROP_COLOR, confColor);
        ObjectSetInteger(0, confName, OBJPROP_ANCHOR, ANCHOR_LEFT);
    }
}

//+------------------------------------------------------------------+
//| Display sentiment information                                    |
//+------------------------------------------------------------------+
void DisplaySentimentInfo()
{
    string sentName = sentimentTextPrefix + IntegerToString(textObjectCounter);
    double price = SymbolInfoDouble(currentSymbol, SYMBOL_BID);
    double offset = -50 * SymbolInfoDouble(currentSymbol, SYMBOL_POINT);
    
    if(ObjectCreate(0, sentName, OBJ_TEXT, 0, TimeCurrent(), price + offset))
    {
        string sentText = "🎭 " + marketSentiment;
        ObjectSetString(0, sentName, OBJPROP_TEXT, sentText);
        ObjectSetString(0, sentName, OBJPROP_FONT, "Arial");
        ObjectSetInteger(0, sentName, OBJPROP_FONTSIZE, 8);
        
        color sentColor = clrSilver;
        if(marketSentiment == "BULLISH") sentColor = clrLime;
        else if(marketSentiment == "BEARISH") sentColor = clrRed;
        
        ObjectSetInteger(0, sentName, OBJPROP_COLOR, sentColor);
        ObjectSetInteger(0, sentName, OBJPROP_ANCHOR, ANCHOR_LEFT);
    }
}

//+------------------------------------------------------------------+
//| Update live analysis display                                     |
//+------------------------------------------------------------------+
void UpdateLiveAnalysisDisplay()
{
    // Create or update live status object
    string statusName = "CryptSIST_LiveStatus";
    
    if(ObjectFind(0, statusName) < 0)
        ObjectCreate(0, statusName, OBJ_LABEL, 0, 0, 0);
    
    // Position in top-right corner
    ObjectSetInteger(0, statusName, OBJPROP_CORNER, CORNER_RIGHT_UPPER);
    ObjectSetInteger(0, statusName, OBJPROP_XDISTANCE, 10);
    ObjectSetInteger(0, statusName, OBJPROP_YDISTANCE, 30);
    
    // Format live status text
    string statusText = StringFormat("🚀 CryptSIST LIVE | %s: %s (%.1f%%) | %s",
                                     currentSymbol, EnumToString(currentSignal),
                                     currentConfidence * 100, marketSentiment);
    
    ObjectSetString(0, statusName, OBJPROP_TEXT, statusText);
    ObjectSetString(0, statusName, OBJPROP_FONT, "Arial Bold");
    ObjectSetInteger(0, statusName, OBJPROP_FONTSIZE, 10);
    
    // Color based on signal
    color statusColor = clrWhite;
    if(currentSignal == SIGNAL_BUY) statusColor = BuyArrowColor;
    else if(currentSignal == SIGNAL_SELL) statusColor = SellArrowColor;
    else if(currentSignal == SIGNAL_HOLD) statusColor = HoldArrowColor;
    
    ObjectSetInteger(0, statusName, OBJPROP_COLOR, statusColor);
    
    // Update time
    string timeText = "⏰ " + TimeToString(TimeCurrent(), TIME_SECONDS);
    string timeName = "CryptSIST_LiveTime";
    
    if(ObjectFind(0, timeName) < 0)
        ObjectCreate(0, timeName, OBJ_LABEL, 0, 0, 0);
    
    ObjectSetInteger(0, timeName, OBJPROP_CORNER, CORNER_RIGHT_UPPER);
    ObjectSetInteger(0, timeName, OBJPROP_XDISTANCE, 10);
    ObjectSetInteger(0, timeName, OBJPROP_YDISTANCE, 50);
    ObjectSetString(0, timeName, OBJPROP_TEXT, timeText);
    ObjectSetString(0, timeName, OBJPROP_FONT, "Arial");
    ObjectSetInteger(0, timeName, OBJPROP_FONTSIZE, 8);
    ObjectSetInteger(0, timeName, OBJPROP_COLOR, clrSilver);
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
        Print("🔧 Will use fallback technical analysis");
        Print("💡 Check server URL: ", ServerURL);
    }
}

//+------------------------------------------------------------------+
//| Clean up old text objects                                       |
//+------------------------------------------------------------------+
void CleanupOldTextObjects()
{
    int cleaned = 0;
    
    for(int i = ObjectsTotal(0) - 1; i >= 0; i--)
    {
        string objName = ObjectName(0, i);
        
        if(StringFind(objName, analysisTextPrefix) >= 0 ||
           StringFind(objName, confidenceTextPrefix) >= 0 ||
           StringFind(objName, sentimentTextPrefix) >= 0)
        {
            // Keep only recent objects
            datetime objTime = (datetime)ObjectGetInteger(0, objName, OBJPROP_TIME);
            if(TimeCurrent() - objTime > 3600) // Older than 1 hour
            {
                ObjectDelete(0, objName);
                cleaned++;
            }
        }
    }
    
    if(cleaned > 0)
        Print("🧹 Cleaned up ", cleaned, " old text objects");
    
    // Reset counter if too high
    if(textObjectCounter > MaxTextObjects * 2)
        textObjectCounter = 0;
}

//+------------------------------------------------------------------+
//| Clean up all text objects                                       |
//+------------------------------------------------------------------+
void CleanupAllTextObjects()
{
    int cleaned = 0;
    
    for(int i = ObjectsTotal(0) - 1; i >= 0; i--)
    {
        string objName = ObjectName(0, i);
        
        if(StringFind(objName, "CryptSIST_") >= 0)
        {
            ObjectDelete(0, objName);
            cleaned++;
        }
    }
    
    if(cleaned > 0)
        Print("🧹 Cleaned up all ", cleaned, " CryptSIST objects");
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
    
    int timeout = 3000; // 3 second timeout
    int res = WebRequest(method, url, headers, timeout, post, result, headers);
    
    if(res == 200)
    {
        return CharArrayToString(result);
    }
    else
    {
        if(res == -1)
        {
            static bool urlWarningShown = false;
            if(!urlWarningShown)
            {
                Print("⚠️ WebRequest error. Add URL to allowed list:");
                Print("Tools -> Options -> Expert Advisors -> Allow WebRequest for:");
                Print(url);
                urlWarningShown = true;
            }
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

double CalculateATR(const MqlRates &rates[], int period)
{
    if(ArraySize(rates) < period + 1) return 0;
    
    double atr = 0;
    for(int i = 1; i <= period; i++)
    {
        int idx1 = ArraySize(rates) - i;
        int idx2 = ArraySize(rates) - i - 1;
        
        double tr = MathMax(rates[idx1].high - rates[idx1].low,
                           MathMax(MathAbs(rates[idx1].high - rates[idx2].close),
                                  MathAbs(rates[idx1].low - rates[idx2].close)));
        atr += tr;
    }
    
    return atr / period;
}
