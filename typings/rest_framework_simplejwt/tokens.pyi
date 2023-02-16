"""
This type stub file was generated by pyright.
"""

from django.conf import settings

class Token:
    """
    A class which validates and wraps an existing JWT or can be used to build a
    new JWT.
    """
    token_type = ...
    lifetime = ...
    def __init__(self, token=..., verify=...) -> None:
        """
        !!!! IMPORTANT !!!! MUST raise a TokenError with a user-facing error
        message if the given token is invalid, expired, or otherwise not safe
        to use.
        """
        ...
    
    def __repr__(self): # -> str:
        ...
    
    def __getitem__(self, key): # -> Any:
        ...
    
    def __setitem__(self, key, value): # -> None:
        ...
    
    def __delitem__(self, key): # -> None:
        ...
    
    def __contains__(self, key): # -> bool:
        ...
    
    def get(self, key, default=...): # -> Any | None:
        ...
    
    def __str__(self) -> str:
        """
        Signs and returns a token as a base64 encoded string.
        """
        ...
    
    def verify(self): # -> None:
        """
        Performs additional validation steps which were not performed when this
        token was decoded.  This method is part of the "public" API to indicate
        the intention that it may be overridden in subclasses.
        """
        ...
    
    def verify_token_type(self): # -> None:
        """
        Ensures that the token type claim is present and has the correct value.
        """
        ...
    
    def set_jti(self): # -> None:
        """
        Populates the configured jti claim of a token with a string where there
        is a negligible probability that the same string will be chosen at a
        later time.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.7
        """
        ...
    
    def set_exp(self, claim=..., from_time=..., lifetime=...): # -> None:
        """
        Updates the expiration time of a token.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.4
        """
        ...
    
    def set_iat(self, claim=..., at_time=...): # -> None:
        """
        Updates the time at which the token was issued.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.6
        """
        ...
    
    def check_exp(self, claim=..., current_time=...): # -> None:
        """
        Checks whether a timestamp value in the given claim has passed (since
        the given datetime value in `current_time`).  Raises a TokenError with
        a user-facing error message if so.
        """
        ...
    
    @classmethod
    def for_user(cls, user): # -> Self@Token:
        """
        Returns an authorization token for the given user that will be provided
        after authenticating the user's credentials.
        """
        ...
    
    _token_backend = ...
    @property
    def token_backend(self): # -> Any:
        ...
    
    def get_token_backend(self): # -> Any:
        ...
    


class BlacklistMixin:
    """
    If the `rest_framework_simplejwt.token_blacklist` app was configured to be
    used, tokens created from `BlacklistMixin` subclasses will insert
    themselves into an outstanding token list and also check for their
    membership in a token blacklist.
    """
    if "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS:
        def verify(self, *args, **kwargs): # -> None:
            ...
        
        def check_blacklist(self): # -> None:
            """
            Checks if this token is present in the token blacklist.  Raises
            `TokenError` if so.
            """
            ...
        
        def blacklist(self): # -> Tuple[BlacklistedToken, bool]:
            """
            Ensures this token is included in the outstanding token list and
            adds it to the blacklist.
            """
            ...
        
        @classmethod
        def for_user(cls, user):
            """
            Adds this token to the outstanding token list.
            """
            ...
        


class SlidingToken(BlacklistMixin, Token):
    token_type = ...
    lifetime = ...
    def __init__(self, *args, **kwargs) -> None:
        ...
    


class AccessToken(Token):
    token_type = ...
    lifetime = ...


class RefreshToken(BlacklistMixin, Token):
    token_type = ...
    lifetime = ...
    no_copy_claims = ...
    access_token_class = AccessToken
    @property
    def access_token(self): # -> access_token_class:
        """
        Returns an access token created from this refresh token.  Copies all
        claims present in this refresh token to the new access token except
        those claims listed in the `no_copy_claims` attribute.
        """
        ...
    


class UntypedToken(Token):
    token_type = ...
    lifetime = ...
    def verify_token_type(self): # -> None:
        """
        Untyped tokens do not verify the "token_type" claim.  This is useful
        when performing general validation of a token's signature and other
        properties which do not relate to the token's intended use.
        """
        ...
    


