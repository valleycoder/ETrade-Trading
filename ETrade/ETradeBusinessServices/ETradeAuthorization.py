import webbrowser

from BusinessModels.Context import Context
from ETrade.ETradeBusinessModels.ETradeInputModel import ETradeInputModel
from ETrade.ETradeBusinessModels.ETradeSettings import ETradeSettings
from ETrade.ETradeBusinessServices.ETradeBusinessService import \
    ETradeBusinessService
from rauth import OAuth1Service, OAuth1Session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from Strings.FormatStringsBase import FormatStringsBase


class ETradeAuthorization(ETradeBusinessService):
    def __init__(self, inputModel: ETradeInputModel, settings: ETradeSettings, 
                    context: Context, strings: FormatStringsBase):
        if strings is None:
            raise ValueError(FormatStringsBase.InputStringsNone)
        self.strings = strings

        if inputModel is None:
            raise ValueError(self.strings.InputNone.format("inputModel"))
        if settings is None:
            raise ValueError(self.strings.InputNone.format("settings"))
        if context is None:
            raise ValueError(self.strings.InputNone.format("context"))

        self.inputModel: ETradeInputModel = inputModel
        self.context: Context = context
        self.settings: ETradeSettings = settings

    def Authorize(self, isCodeEntryManual:bool = True, chromeDriverExecutablePath:str = ""):
        if isCodeEntryManual is False and chromeDriverExecutablePath == "":
            raise ValueError(self.strings.InputNone.format("chromeDriverExecutablePath"))

        etrade = OAuth1Service(
            name="etrade",
            base_url=self.settings.BaseUrl,
            consumer_key= self.settings.ConsumerKey,
            consumer_secret=self.settings.ConsumerSecret,
            request_token_url=self.settings.RequestTokenUrl,
            authorize_url=self.settings.AuthorizeUrl,
            access_token_url=self.settings.AccessTokenUrl,
        )

        # Step 1: Get OAuth 1 request token and secret
        request_token, request_token_secret = etrade.get_request_token(
            params={"oauth_callback": "oob", "format": "json"})

        # Step 2: Go through the authentication flow. Login to E*TRADE.
        # After you login, the page will provide a text code to enter.
        authorize_url = etrade.authorize_url.format(etrade.consumer_key, request_token)

        text_code = ""
        if isCodeEntryManual is True:
            webbrowser.open(authorize_url)
            text_code = input("Please accept agreement and enter text code from browser: ")
        else:            
            text_code = self.GetOAuthVerifierCode(authorize_url, chromeDriverExecutablePath)

        # Step 3: Exchange the authorized request token for an authenticated OAuth 1 session
        accessToken = etrade.get_access_token(request_token,
                                  request_token_secret,
                                  params={"oauth_verifier": text_code})   
                                     
        return accessToken

    def GetOAuthVerifierCode(self, authorizeUrl:str, chromeDriverExecutablePath:str):
        options = webdriver.ChromeOptions() 
        options.add_argument("start-maximized")
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(executable_path = chromeDriverExecutablePath, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        # chrome_options.add_argument("--headless")

        """
        driver = webdriver.Remote(
        'localhost:9515', desired_capabilities=options.to_capabilities())
        
        script = '''
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        '''
        driver.execute_script(script)
        """

        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'})
        # driver.execute_cdp_cmd("Network.enable", {})
        # driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browser"}})

        # exit(0)
        driver.get(authorizeUrl)

        WebDriverWait(driver, 60).until(expected_conditions.presence_of_element_located((By.ID, "user_orig")))
        
        userName = driver.find_element_by_id("user_orig")
        userName.clear()
        userName.send_keys(self.settings.AccountUserName)
        password = driver.find_element_by_name("PASSWORD")
        password.clear()
        password.send_keys(self.settings.AccountPassword)
        logon = driver.find_element_by_id("logon_button")
        # logon = driver.find_element_by_xpath("/html/body/div[2]/div/div/div/div[2]/section/section/div/div/div[1]/div/section/div/div[1]/div/div/form/div[5]/div[2]/button")
        logon.click()
        # print(driver.execute_script("return document['$cdc_asdjflasutopfhvcZLmcfl_']"))

        # time.sleep(60)
        WebDriverWait(driver, 60).until(expected_conditions.presence_of_element_located((By.NAME, "submit")))
        accept = driver.find_elements_by_name("submit")
        for obj in accept:
            if obj.get_attribute("value") == "Accept":
                obj.click()
                break
        
        WebDriverWait(driver, 60).until(expected_conditions.presence_of_element_located((By.TAG_NAME, "input")))
        codeElement = driver.find_element_by_tag_name("input")
        text_code = codeElement.get_attribute("value")
        driver.close()
        return text_code

    def RenewAccessToken(self, accessToken:str = None, accessTokenSecret:str = None):              
        refreshSession = OAuth1Session(
            self.settings.ConsumerKey,
            self.settings.ConsumerSecret,
            access_token = self.inputModel.AccessToken if accessToken is None else accessToken,
            access_token_secret = self.inputModel.AccessTokenSecret if accessTokenSecret is None else accessTokenSecret
        )

        resp = refreshSession.get(self.settings.AccessTokenRenewUrl, header_auth=True)
        refreshSession.close()
        return resp.status_code
