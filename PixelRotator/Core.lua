local playerClass = "UNKNOWN"
local isDK = false
local f = CreateFrame("Frame", "PixelReaderFrame", WorldFrame)
f:SetSize(86, 10)
f:SetPoint("TOPLEFT", 0, 0)
f:SetFrameStrata("TOOLTIP")
f:SetFrameLevel(9999)

local NUM_PIXELS = 43
local BLOCK_SIZE = 2

local function CreateTextureRow(parent, yOffset)
    local textures = {}
    for i = 1, NUM_PIXELS do
        local tex = parent:CreateTexture(nil, "OVERLAY")
        tex:SetSize(BLOCK_SIZE, BLOCK_SIZE)
        tex:SetPoint("TOPLEFT", (i-1)*BLOCK_SIZE, -yOffset*BLOCK_SIZE)
        tex:SetColorTexture(0, 0, 0, 1)
        textures[i] = tex
    end
    return textures
end

local offRow1 = CreateTextureRow(f, 0)
local offRow2 = CreateTextureRow(f, 1)
local defRow1 = CreateTextureRow(f, 2)
local defRow2 = CreateTextureRow(f, 3)
local intRow1 = CreateTextureRow(f, 4)
local intRow2 = CreateTextureRow(f, 5)
local hpRow   = CreateTextureRow(f, 6)

-- Kalibracja dla paska HP (act_type = 7 => binarne 111)
hpRow[1]:SetColorTexture(0, 0, 1, 1) -- Blue anchor
hpRow[2]:SetColorTexture(1, 1, 1, 1) -- White (Luma 1)
hpRow[3]:SetColorTexture(0, 0, 0, 1) -- Black (Luma 0)
hpRow[4]:SetColorTexture(1, 1, 1, 1) -- Bit 1
hpRow[5]:SetColorTexture(1, 1, 1, 1) -- Bit 2
hpRow[6]:SetColorTexture(1, 1, 1, 1) -- Bit 3
-- hpRow[7] bedzie ustawiane w OnUpdate
hpRow[43]:SetColorTexture(0, 1, 0, 1) -- Green anchor (BARDZO WAZNE DLA PYTHONA!)

local hpBar = CreateFrame("StatusBar", nil, f)
hpBar:SetPoint("TOPLEFT", hpRow[8], "TOPLEFT")
hpBar:SetPoint("BOTTOMRIGHT", hpRow[42], "BOTTOMRIGHT")
hpBar:SetStatusBarTexture("Interface\\Buttons\\WHITE8x8")
hpBar:SetStatusBarColor(1, 0, 0, 1) -- Czerwony

f:Show()

local KeyToID = {
    ["1"] = 1, ["2"] = 2, ["3"] = 3, ["4"] = 4, ["5"] = 5,
    ["6"] = 6, ["7"] = 7, ["8"] = 8, ["9"] = 9, ["0"] = 10,
    ["-"] = 11, ["="] = 12,
    ["A"] = 20, ["B"] = 21, ["C"] = 22, ["D"] = 23, ["E"] = 24, ["F"] = 25, ["G"] = 26,
    ["H"] = 27, ["I"] = 28, ["J"] = 29, ["K"] = 30, ["L"] = 31, ["M"] = 32, ["N"] = 33,
    ["O"] = 34, ["P"] = 35, ["Q"] = 36, ["R"] = 37, ["S"] = 38, ["T"] = 39, ["U"] = 40,
    ["V"] = 41, ["W"] = 42, ["X"] = 43, ["Y"] = 44, ["Z"] = 45,
    ["TAB"] = 71, ["SPACE"] = 70,
    ["F1"] = 50, ["F2"] = 51, ["F3"] = 52, ["F4"] = 53, ["F5"] = 54, ["F6"] = 55,
    ["F7"] = 56, ["F8"] = 57, ["F9"] = 58, ["F10"] = 59, ["F11"] = 60, ["F12"] = 61,
    ["BUTTON3"] = 80, ["BUTTON4"] = 81, ["BUTTON5"] = 82,
    ["NUMPAD1"] = 91, ["NUMPAD2"] = 92, ["NUMPAD3"] = 93, ["NUMPAD4"] = 94, ["NUMPAD5"] = 95,
    ["NUMPAD6"] = 96, ["NUMPAD7"] = 97, ["NUMPAD8"] = 98, ["NUMPAD9"] = 99, ["NUMPAD0"] = 90,
    ["NUMPADPLUS"] = 100, ["NUMPADMINUS"] = 101, ["NUMPADMULTIPLY"] = 102, ["NUMPADDIVIDE"] = 103,
}

local function ParseBinding(bindingStr)
    if not bindingStr then return 0, 0 end
    local shift = string.find(bindingStr, "SHIFT%-") and 1 or 0
    local ctrl = string.find(bindingStr, "CTRL%-") and 2 or 0
    local alt = string.find(bindingStr, "ALT%-") and 4 or 0
    local baseKey = bindingStr:match("([^-]+)$")
    if not baseKey then return 0, 0 end
    local keyID = KeyToID[baseKey:upper()] or 0
    return keyID, (shift + ctrl + alt)
end

local function WriteBits(rowA, rowB, startIdx, value, numBits)
    local v = value
    for i = 0, numBits - 1 do
        local b = v % 2
        rowA[startIdx + i]:SetColorTexture(b, b, b, 1)
        rowB[startIdx + i]:SetColorTexture(b, b, b, 1)
        v = math.floor(v / 2)
    end
end

local function RenderAction(target, rowA, rowB, actionType)
    if not target then 
        for i = 1, NUM_PIXELS do 
            rowA[i]:SetColorTexture(0, 0, 0, 1) 
            rowB[i]:SetColorTexture(0, 0, 0, 1) 
        end
        return 
    end

    local id = target.spellID or target.itemID
    if not id then return end

    local aType = target.spellID and "spell" or "item"
    local name = ""
    
    if aType == "spell" then
        if C_Spell and C_Spell.GetSpellInfo then
            local info = C_Spell.GetSpellInfo(id)
            if info then name = info.name end
        else
            name = (GetSpellInfo and GetSpellInfo(id)) or ""
        end
    else
        name = (GetItemInfo and GetItemInfo(id)) or ""
    end

    local targetName = name
    local bestScore = -1
    local bestSlotKey = 0
    local bestSlotMod = 0
    
    -- 1. NAJPIERW BIERZEMY Z JUSTAC DIRECT (priorytetyzowanie faktycznego hotkeya addonowego)
    local justKey = target.cachedHotkey or (target.hotkeyText and target.hotkeyText:GetText())
    if justKey and justKey ~= "" then
        local kID, mMask = ParseBinding(justKey)
        if kID > 0 then
            bestScore, bestSlotKey, bestSlotMod = 999, kID, mMask
        end
    end
    
    -- 2. JEŚLI JUSTAC NIE ZNA BINDY, SKANUJEMY SLOTY (Fallback)
    if bestScore < 0 and targetName ~= "" then
        local targetMatch = targetName:lower():gsub("%s+", "")
        for slot = 1, 120 do
            local actionType, actionID = GetActionInfo(slot)
            local spellName = ""
            if actionType == "spell" and actionID then
                local info = C_Spell.GetSpellInfo(actionID)
                if info then spellName = info.name end
            elseif actionType == "macro" then
                local mName = GetActionText(slot) or ""
                local sName = GetMacroSpell(mName)
                if sName then spellName = sName else spellName = mName end
            end
            
            if spellName and tostring(spellName):lower():gsub("%s+", "") == targetMatch then
                local bCmd = "ACTIONBUTTON" .. slot
                if slot >= 37 and slot <= 48 then bCmd = "MULTIACTIONBAR1BUTTON" .. (slot-36)
                elseif slot >= 49 and slot <= 60 then bCmd = "MULTIACTIONBAR2BUTTON" .. (slot-48)
                elseif slot >= 25 and slot <= 36 then bCmd = "MULTIACTIONBAR3BUTTON" .. (slot-24)
                elseif slot >= 61 and slot <= 72 then bCmd = "MULTIACTIONBAR4BUTTON" .. (slot-60)
                end
                
                local key1 = GetBindingKey(bCmd)
                if key1 then
                    local kID, mMask = ParseBinding(key1)
                    if kID > 0 then
                        local score = 1
                        if key1:find("SHIFT-") then score = 100
                        elseif key1:find("CTRL-") then score = 10
                        elseif key1:find("ALT-") then score = 5 end
                        if score > bestScore then
                            bestScore, bestSlotKey, bestSlotMod = score, kID, mMask
                        end
                    end
                end
            end
        end

    end

    if bestScore >= 0 then
        -- 1. Anchor (Niebieski)
        rowA[1]:SetColorTexture(0, 0, 1, 1)
        rowB[1]:SetColorTexture(0, 0, 1, 1)

        -- 2. Szerokosc kalibracyjna - BIALY
        rowA[2]:SetColorTexture(1, 1, 1, 1)
        rowB[2]:SetColorTexture(1, 1, 1, 1)

        -- 3. Zakonczenie p_width - CZARNY
        rowA[3]:SetColorTexture(0, 0, 0, 1)
        rowB[3]:SetColorTexture(0, 0, 0, 1)

        -- 4-6. Typ akcji (3 bity)
        WriteBits(rowA, rowB, 4, actionType, 3)

        -- 7-9. Mod Mask (3 bity)
        WriteBits(rowA, rowB, 7, bestSlotMod, 3)

        -- 10-17. Key ID (8 bitów)
        WriteBits(rowA, rowB, 10, bestSlotKey, 8)

        -- 18-41. Spell ID (24 bity)
        WriteBits(rowA, rowB, 18, id, 24)

        -- 42. Heartbeat (1 bit, mrugajacy 0/1)
        local hb = (math.sin(GetTime()*10) > 0) and 1 or 0
        WriteBits(rowA, rowB, 42, hb, 1)
        
        -- 43. Zakonczenie kalibracyjne (Zielony)
        rowA[43]:SetColorTexture(0, 1, 0, 1)
        rowB[43]:SetColorTexture(0, 1, 0, 1)
        return
    end

    -- Jeśli pętla się skończy i nic nie wysłaliśmy:
    for i = 1, NUM_PIXELS do 
        rowA[i]:SetColorTexture(0, 0, 0, 1) 
        rowB[i]:SetColorTexture(0, 0, 0, 1) 
    end
end

local throttle = 0
f:SetScript("OnUpdate", function(self, elapsed)
    throttle = throttle + elapsed
    if throttle < 0.05 then return end
    throttle = 0
    
    -- Odświeżamy detekcję klasy (bezpieczniejsze niż jednorazowy odczyt przy starcie)
    local _, pClass = UnitClass("player")
    if pClass then 
        playerClass = pClass
        isDK = (playerClass == "DEATHKNIGHT")
    end
    hpRow[7]:SetColorTexture(isDK and 1 or 0, isDK and 1 or 0, isDK and 1 or 0, 1)
    
    if UnitHealth and UnitHealthMax then
        hpBar:SetMinMaxValues(0, UnitHealthMax("player") or 1)
        hpBar:SetValue(UnitHealth("player") or 0)
    end

    local LibStub = _G.LibStub
    if not LibStub then return end
    local AceAddon = LibStub("AceAddon-3.0", true)
    if not AceAddon then return end
    local ok, addon = pcall(AceAddon.GetAddon, AceAddon, "JustAssistedCombat", true)
    if not ok or not addon then return end
    
    local function IsReallyTarget(frame, isOffensive)
        if not frame then return false end
        
        if isOffensive then return true end
        
        local hasGlow = frame.hasAssistedGlow or frame.hasDefensiveGlow or frame.hasInterruptGlow or frame.defShowGlow or frame.hasProcGlow
        
        local hasGlow = frame.hasAssistedGlow or frame.hasDefensiveGlow or frame.hasInterruptGlow or frame.defShowGlow or frame.hasProcGlow
        
        if hasGlow then return true end
        
        return false
    end
    
    -- TWARDY RESET (Tylko rzędy akcji, HP ma swoje własne stałe kotwice)
    local rows = {offRow1, offRow2, defRow1, defRow2, intRow1, intRow2}
    for _, prow in ipairs(rows) do
        if prow then
            for i = 1, NUM_PIXELS do prow[i]:SetColorTexture(0, 0, 0, 1) end
        end
    end

    local offTarget = IsReallyTarget(addon.spellIcons and addon.spellIcons[1], true) and addon.spellIcons[1]
    local defTarget1 = IsReallyTarget(addon.defensiveIcons and addon.defensiveIcons[1], false) and addon.defensiveIcons[1]
    local function IsActionReady(target)
        if not target then return false end
        local id = target.spellID or target.itemID
        if not id then return true end
        
        if target.spellID then
            local info = nil
            if C_Spell and C_Spell.GetSpellCooldown then
                info = C_Spell.GetSpellCooldown(id)
            end
            
            if info and type(info) == "table" then
                -- FLAGI LOGICZNE (Safe check): Prawdziwy cooldown jest wtedy, gdy spell jest w trakcie (isActive)
                -- i NIE jest to tylko Global Cooldown (not isOnGCD).
                if info.isActive and not info.isOnGCD then
                    return false -- Na CD (nie-GCD)
                end
            else
                -- Fallback dla starszych wersji gry (nie-Retail)
                local startTime, duration = GetSpellCooldown(id)
                if startTime and startTime > 0 and duration and duration > 1.5 then
                    return false
                end
            end
        elseif target.itemID then
            -- Dla itemów, jeśli JustAC pokazał ikonę, a my nie możemy bezpiecznie sprawdzić CD (SecretNumbers),
            -- to ufamy że JustAC wie co robi lub sprawdzamy wizualny element cooldownu.
            if target.cooldown and target.cooldown:IsShown() then
                return false
            end
        end
        return true
    end

    local offTarget = IsReallyTarget(addon.spellIcons and addon.spellIcons[1], true) and addon.spellIcons[1]
    local defTarget1 = IsReallyTarget(addon.defensiveIcons and addon.defensiveIcons[1], false) and addon.defensiveIcons[1]
    local intTarget = IsReallyTarget(addon.interruptIcon, false) and addon.interruptIcon
    
    -- Filtrujemy akcje przez sprawdzanie Cooldownu (CD)
    if not IsActionReady(offTarget) then offTarget = nil end
    if not IsActionReady(defTarget1) then defTarget1 = nil end
    if not IsActionReady(intTarget) then intTarget = nil end

    RenderAction(offTarget, offRow1, offRow2, 1)
    RenderAction(defTarget1, defRow1, defRow2, 2)
    RenderAction(intTarget, intRow1, intRow2, 5)
end)

-- Komenda Debugująca
SLASH_PIXELROTATOR1 = "/pr"
SlashCmdList["PIXELROTATOR"] = function(msg)
    msg = (msg or ""):match("^%s*(.-)%s*$"):lower()
    if msg == "" then
        print("|cffffff00[PixelRotator] Pełna diagnostyka JustAC...|r")
        local LibStub = _G.LibStub
        local AceAddon = LibStub and LibStub("AceAddon-3.0", true)
        local ok, addon = pcall(AceAddon.GetAddon, AceAddon, "JustAssistedCombat", true)
        
        if not ok or not addon then 
            print("|cffff0000Błąd: JustAssistedCombat nie został znaleziony!|r")
            return 
        end

        local function DebugTarget(label, target)
            if not target then
                print(label .. ": |cffaaaaaaBrak sugestii|r")
                return
            end
            local glow = target.hasAssistedGlow or target.hasDefensiveGlow or target.hasInterruptGlow
            local glowStr = glow and "|cff00ff00TAK|r" or "|cffff0000NIE|r"
            local visStr = target:IsVisible() and "|cff00ff00TAK|r" or "|cffff0000NIE|r"
            local name = "Nieznany"
            if target.spellID then
                local info = C_Spell.GetSpellInfo(target.spellID)
                if info then name = info.name end
            end
            local key = target.cachedHotkey or "Brak w JustAC"
            
            print(label .. ": |cff00ffff" .. name .. "|r | Glow: " .. glowStr .. " | Vis: " .. visStr .. " | Key: |cffffff00" .. key .. "|r")
        end

        DebugTarget("[OFFENSE]", addon.spellIcons and addon.spellIcons[1])
        DebugTarget("[DEFENSE]", addon.defensiveIcons and addon.defensiveIcons[1])
        DebugTarget("[INTERRUPT]", addon.interruptIcon)
        
        print("|cff00d4ff[PixelRotator]|r Class English: " .. (playerClass or "NIL") .. " | isDK: " .. (isDK and "YES" or "NO"))
        print("|cffaaaaaaWpisz /pr find [Klucz] (np. /pr find S-Q), aby sprawdzić bindowanie slotu.|r")
        print("|cffaaaaaaWpisz /pr hp aby sprawdzić jak gra odczytuje Twoje zdrowie.|r")
        print("|cffaaaaaaWpisz /pr debug aby sprawdzić wykrywanie klasy przez bota.|r")
    elseif msg == "debug" then
        print("|cff00d4ff[PixelRotator]|r Class English: " .. (playerClass or "NIL") .. " | isDK: " .. (isDK and "YES" or "NO"))
    elseif msg == "hp" then
        print("|cffffff00[PixelRotator] Diagnostyka Zdrowia:|r")
        
        local ok1, hp1 = pcall(UnitHealth, "player")
        print("UnitHealth: " .. tostring(ok1) .. " Type: " .. type(hp1) .. " Value: " .. tostring(hp1))
        
        local ok2, mhp2 = pcall(UnitHealthMax, "player")
        print("UnitHealthMax: " .. tostring(ok2) .. " Type: " .. type(mhp2) .. " Value: " .. tostring(mhp2))
        
        if UnitPercentHealthFromGUID then
            local ok3, php3 = pcall(UnitPercentHealthFromGUID, UnitGUID("player"))
            print("UnitPercentHealthFromGUID: " .. tostring(ok3) .. " Type: " .. type(php3) .. " Value: " .. tostring(php3))
        end
        
        print("UI Widget Dumps:")
        if PlayerFrameHealthBar then
            local val = PlayerFrameHealthBar:GetValue()
            print("PlayerFrameHealthBar:GetValue() -> " .. tostring(val))
        else
            print("PlayerFrameHealthBar: nil")
        end
        
        if PlayerFrame and PlayerFrame.healthbar then
            local val = PlayerFrame.healthbar:GetValue()
            print("PlayerFrame.healthbar:GetValue() -> " .. tostring(val))
        end
        
    elseif msg:find("^find") then
        local searchKey = msg:sub(6):upper():gsub("+", "-")
        if searchKey == "" then
            print("|cffff0000Użycie: /pr find [Klucz] lub /pr find [Nazwa]|r")
            return
        end

        print("|cffffff00[PixelRotator] Szukanie: " .. searchKey .. "|r")
        local found = false
        local foundCount = 0
        
        for slot = 1, 180 do
            local actionType, actionID = GetActionInfo(slot)
            local currentName = ""
            
            if actionID and actionID > 0 then
                if actionType == "spell" then
                    local info = C_Spell.GetSpellInfo(actionID)
                    if info then currentName = info.name end
                elseif actionType == "macro" then
                    local mName = GetMacroInfo(actionID)
                    local sName = GetMacroSpell(mName)
                    currentName = sName or mName or ""
                elseif actionType == "item" then
                    currentName = GetItemInfo(actionID) or ""
                end
            end

            local bCmd = "ACTIONBUTTON" .. slot
            if slot >= 37 and slot <= 48 then bCmd = "MULTIACTIONBAR1BUTTON" .. (slot - 36)
            elseif slot >= 25 and slot <= 36 then bCmd = "MULTIACTIONBAR2BUTTON" .. (slot - 24)
            elseif slot >= 49 and slot <= 60 then bCmd = "MULTIACTIONBAR3BUTTON" .. (slot - 48)
            elseif slot >= 61 and slot <= 72 then bCmd = "MULTIACTIONBAR4BUTTON" .. (slot - 60)
            elseif slot >= 73 and slot <= 84 then bCmd = "MULTIACTIONBAR5BUTTON" .. (slot - 72)
            end
            
            local k1, k2 = GetBindingKey(bCmd)
            local matchByName = currentName ~= "" and currentName:lower():find(searchKey:lower(), 1, true)
            local matchByKey = (k1 and k1:upper() == searchKey) or (k2 and k2:upper() == searchKey)

            if matchByName or matchByKey then
                foundCount = foundCount + 1
                local bindStr = k1 or "|cffff0000BRAK|r"
                print("|cff00ff00[" .. foundCount .. "] Slot: " .. slot .. "|r | Nazwa: |cffffff00" .. currentName .. "|r | BIND: |cff00ffff" .. bindStr .. "|r")
                found = true
            end
        end
        
        if not found then 
            print("|cffff0000Nie znaleziono żadnego slotu pasującego do: " .. searchKey .. "|r") 
        end
    end
end

