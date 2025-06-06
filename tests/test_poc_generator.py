import pytest
from unittest.mock import Mock, patch
from app.ai.services.poc_generator import POCGenerator
from app.ai.services.model_manager import ModelManager
from app.ai.services.prompt_manager import PromptManager

@pytest.fixture
def mock_model_manager():
    return Mock(spec=ModelManager)

@pytest.fixture
def mock_prompt_manager():
    return Mock(spec=PromptManager)

@pytest.fixture
def poc_generator(mock_model_manager, mock_prompt_manager):
    return POCGenerator(
        model_manager=mock_model_manager,
        prompt_manager=mock_prompt_manager,
        output_dir="test_pocs"
    )

@pytest.mark.asyncio
async def test_generate_poc(poc_generator, mock_model_manager, mock_prompt_manager):
    # Mock data
    cve_id = "CVE-2023-1234"
    description = "Test vulnerability"
    vulnerability_type = "SQL Injection"
    affected_component = "Database"
    
    # Mock prompt manager response
    mock_prompt_manager.format_prompt.return_value = "Test prompt"
    
    # Mock model response
    mock_response = """
    ```python
    # Test PoC code
    def exploit():
        print("Test exploit")
    ```
    
    # Documentation
    ## Dependencies
    - Python 3.8+
    
    ## Setup
    Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    
    ## Usage
    Run the exploit:
    ```bash
    python poc.py
    ```
    
    ## Safety Warning
    This is a test PoC. Use responsibly.
    """
    mock_model_manager.generate.return_value = mock_response
    
    # Test PoC generation
    result = await poc_generator.generate_poc(
        cve_id=cve_id,
        description=description,
        vulnerability_type=vulnerability_type,
        affected_component=affected_component
    )
    
    # Verify result
    assert result["cve_id"] == cve_id
    assert "code" in result
    assert "documentation" in result
    assert "metadata" in result
    
    # Verify calls
    mock_prompt_manager.format_prompt.assert_called_once()
    mock_model_manager.generate.assert_called_once()

@pytest.mark.asyncio
async def test_get_poc(poc_generator):
    # Mock data
    cve_id = "CVE-2023-1234"
    
    # Test getting non-existent PoC
    result = await poc_generator.get_poc(cve_id)
    assert result is None

@pytest.mark.asyncio
async def test_list_pocs(poc_generator):
    # Test listing PoCs
    pocs = poc_generator.list_pocs()
    assert isinstance(pocs, list)

@pytest.mark.asyncio
async def test_validate_poc(poc_generator):
    # Mock data
    cve_id = "CVE-2023-1234"
    
    # Test validating non-existent PoC
    with pytest.raises(Exception):
        await poc_generator.validate_poc(cve_id) 