import datetime
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient, CertificatePolicy
from azure.keyvault.certificates._models import KeyProperties
from azure.core.exceptions import HttpResponseError

# ----------------------------------------------------------------------------------------------------------
# Prerequistes -
#
# 1. An Azure Key Vault-
#    https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli
#
#  2. Microsoft Azure Key Vault PyPI package -
#    https://pypi.python.org/pypi/azure-keyvault-certificates/
#
# 3. Microsoft Azure Identity package -
#    https://pypi.python.org/pypi/azure-identity/
#
# 4. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_URL.
# How to do this - https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets#createget-credentials)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a vault(certificate) resource for Azure Key Vault
#
# 1. Create a new certificate (create_certificate)
#
# 2. Get an existing certificate (get_certificate)
#
# 3. Update an existing certificate (update_certificate)
#
# 4. Delete a certificate (delete_certificate)
#
# ----------------------------------------------------------------------------------------------------------

def run_sample():
    # Instantiate a certificate client that will be used to call the service.
    # Notice that the client is using default Azure credentials.
    # To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
    # 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = CertificateClient(vault_url=VAULT_URL, credential=credential)
    try:
        # Let's create a certificate for holding bank account credentials valid for 1 year.
        # if the certificate already exists in the Key Vault, then a new version of the certificate is created.
        print("\n1. Create Certificate")

        # Before creating your certificate, let's create the management policy for your certificate.
        # Here you specify the properties of the key, secret, and issuer backing your certificate,
        # the X509 component of your certificate, and any lifetime actions you would like to be taken
        # on your certificate
        cert_policy = CertificatePolicy(key_properties=KeyProperties(exportable=True,
                                                                     key_type='RSA',
                                                                     key_size=2048,
                                                                     reuse_key=False),
                                        content_type='application/x-pkcs12',
                                        issuer_name='Self',
                                        subject_name='CN=*.microsoft.com',
                                        san_dns_names=['onedrive.microsoft.com', 'xbox.microsoft.com'],
                                        validity_in_months=24
                                        )
        cert_name="BankCertificate"
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=365)
        print("right before create")
        certificate_operation = client.create_certificate(name=cert_name, policy=cert_policy, expires=expires)
        print("Certificate with name '{0}' created".format(certificate_operation.name))

        # Let's get the bank certificate using its name
        print("\n2. Get a Certificate by name")
        bank_certificate = client.get_certificate(name=certificate_operation.name)
        print("Certificate with name '{0}' was found with expiration date '{1}'.".format(bank_certificate.name, bank_certificate.expires))

        # After one year, the bank account is still active, we need to update the expiry time of the certificate.
        # The update method can be used to update the expiry attribute of the certificate.
        print("\n3. Update a Certificate by name")
        expires = bank_certificate.expires + datetime.timedelta(days=365)
        updated_certificate = client.update_certificate(name=bank_certificate.name, expires=expires)
        print("Certificate with name '{0}' was updated on date '{1}'".format(bank_certificate.name, updated_certificate.updated))
        print("Certificate with name '{0}' was updated to expire on '{1}'".format(bank_certificate.name, updated_certificate.expires))

        # The bank account was closed, need to delete its credentials from the Key Vault.
        print("\n4. Delete Certificate")
        deleted_certificate = client.delete_certificate(name=bank_certificate.name)
        print("Deleting Certificate..")
        print("Certificate with name '{0}' was deleted.".format(bank_certificate.name))

    except HttpResponseError as e:
        print("\nrun_sample has caught an error. {0}".format(e.message))

    finally:
        print("\nrun_sample done")


if __name__ == "__main__":
    try:
        run_sample()

    except Exception as e:
        print("Top level Error: {0}".format(str(e)))